Buenas preguntas — las tres van al corazón de cualquier arquitectura AWS. Te las
  respondo con detalle.

  ---
  1️⃣  ¿Cómo se consume Bedrock en esta solución?

  En ShopMind, Bedrock se consume en DOS puntos distintos (y es clave entender la
  diferencia, porque son servicios separados):

  🔵 Punto A — Bedrock Runtime (para invocar el LLM Nova Pro)

  Esto pasa dentro del agente, cuando Strands necesita "pensar".

  # app/agents/supervisor_agent.py:24
  _agent = Agent(
      model="us.amazon.nova-pro-v1:0",   # ← acá se pide Nova Pro
      system_prompt="...",
      tools=[mcp_client],
  )

  ¿Qué pasa por debajo? Strands usa boto3 internamente para llamar a la API
  bedrock-runtime:InvokeModel (o Converse). Vos no ves el cliente boto3 porque Strands lo
   abstrae, pero está ahí.

  El string "us.amazon.nova-pro-v1:0" es un inference profile (empieza con us.) que rutea
   la llamada a la región más cercana con capacidad — optimiza latencia y throughput.

  🔵 Punto B — Bedrock AgentCore (para invocar al agente desplegado)

  Esto pasa en el backend proxy, cuando quiere hablar con el agente que vive en el
  runtime de AgentCore.

  # app/backend.py:27
  session = boto3.Session(profile_name="chile", region_name="us-east-1")
  bedrock_rt = session.client("bedrock-agentcore")   # ← cliente distinto

  response = bedrock_rt.invoke_agent_runtime(         # ← API distinta
      agentRuntimeArn=AGENT_ARN,
      payload=json.dumps({"message": req.message, ...}),
  )

  Clave didáctica para memorizar:

  ┌─────────────────────────┬───────────────────────────┬────────────────────────────┐
  │        Servicio         │       Client boto3        │          Qué hace          │
  ├─────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Bedrock Runtime         │ bedrock-runtime           │ Invoca modelos (Nova,      │
  │                         │                           │ Claude)                    │
  ├─────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Bedrock AgentCore       │ bedrock-agentcore         │ Invoca agentes desplegados │
  ├─────────────────────────┼───────────────────────────┼────────────────────────────┤
  │ Bedrock AgentCore       │ bedrock-agentcore-control │ CRUD de agentes, gateways  │
  │ Control                 │                           │                            │
  └─────────────────────────┴───────────────────────────┴────────────────────────────┘

  Son tres APIs distintas dentro de Bedrock. La confusión típica es pensar que AgentCore
  "es Bedrock" — no, AgentCore usa Bedrock internamente para el LLM, pero es su propio
  servicio.

  ---
  2️⃣  ¿Hay un rol? → Sí, tres roles IAM

  Rol 1: ShopMindAgentCoreRole (el más importante)

  Lo asume el agente cuando corre dentro de AgentCore Runtime. Necesita:
  - bedrock:InvokeModel sobre
  arn:aws:bedrock:*:*:inference-profile/us.amazon.nova-pro-v1:0
  - bedrock-agentcore:* (para memoria, gateway, etc.)
  - Permisos a CloudWatch Logs, X-Ray (observabilidad)

  Importante: este rol NO tiene credenciales de usuario; AgentCore se lo inyecta al
  contenedor. Por eso tu supervisor_agent.py no hace boto3.Session(profile=...) — corre
  con el rol asumido.

  Rol 2: ShopMindLambdaRole

  Lo asume la Lambda shopmind-tools. Necesita solo permisos básicos (logs) + lo que la
  tool necesite.

  Rol 3: ShopMindGatewayRole

  Lo asume AgentCore Gateway para invocar la Lambda target.

  🔑 Local vs Production: las credenciales vienen de lugares distintos

  ┌───────────────────────────────────────────┬──────────────────────────────────────┐
  │                   Modo                    │      De dónde saca credenciales      │
  ├───────────────────────────────────────────┼──────────────────────────────────────┤
  │ backend_local.py (tu laptop)              │ AWS_PROFILE=chile →                  │
  │                                           │ ~/.aws/credentials                   │
  ├───────────────────────────────────────────┼──────────────────────────────────────┤
  │ backend.py (tu laptop llamando a          │ AWS_PROFILE=chile                    │
  │ AgentCore)                                │                                      │
  ├───────────────────────────────────────────┼──────────────────────────────────────┤
  │ Agente corriendo en AgentCore             │ Rol IAM asumido automáticamente      │
  ├───────────────────────────────────────────┼──────────────────────────────────────┤
  │ Lambda shopmind-backend                   │ Rol de la Lambda (via Function URL)  │
  └───────────────────────────────────────────┴──────────────────────────────────────┘

  ---
  3️⃣  ¿Variables de entorno?

  Backend (Python)

  AWS_PROFILE=chile              # solo en local
  AWS_DEFAULT_REGION=us-east-1
  # No hay API keys — todo pasa por IAM

  Notá: NO hay BEDROCK_API_KEY ni nada parecido. Bedrock usa SigV4 (firma AWS nativa con
  tus credenciales IAM). Esa es una gran ventaja vs OpenAI/Anthropic-directo, que
  requieren API keys que hay que rotar, guardar en Secrets Manager, etc.

  Frontend (Vite)

  VITE_AGENT_ARN=arn:aws:bedrock-agentcore:us-east-1:703671890483:runtime/shopmind_superv
  isor-tbOrpEGt4K
  VITE_REGION=us-east-1
  VITE_AGENT_URL=https://a2zl7p4o74quihzcceh5luqb7a0vkgqp.lambda-url.us-east-1.on.aws

  Hardcodeos que vale la pena sacar si esto fuera prod

  Hoy el código tiene cosas atadas (para demo está bien, pero en la charla te pueden
  preguntar):
  - backend.py:14 → AGENT_ARN hardcoded
  - backend.py:16 → AWS_PROFILE="chile" hardcoded
  - backend_lambda/handler.py:9 → TOOLS_LAMBDA = "shopmind-tools" hardcoded

  En producción: todo iría como env vars de Lambda o Parameter Store / Secrets Manager.

  ---
  4️⃣  ¿Qué tan portable es el MVP?

  Respuesta corta: poco portable. Es AWS-native de punta a punta.

  Te lo divido en capas, de más a menos portable:

  🟢 Portable (cambiás 0 líneas)

  - Frontend React/Vite — HTML + JS puro, podés servirlo en Vercel, Netlify, Cloudflare
  Pages, GitHub Pages.
  - Puppeteer scraper (scraper.js) — Node + headless Chrome, corre en cualquier lado.
  - FastAPI backend — Python estándar, corre en cualquier VM.

  🟡 Portable con cambios menores

  - Strands Agents — es open source y soporta otros providers (OpenAI, Anthropic directo,
   Ollama). Cambiás model="us.amazon.nova-pro-v1:0" por
  model="anthropic/claude-3-5-sonnet" y un env var de API key.
  - MCP Server (mcp_server.py) — protocolo abierto, corre en cualquier lado.
  - Tools (tools_local.py) — Python puro, no tocan AWS.

  🔴 No portable (atado a AWS)

  - AgentCore Runtime — no tiene equivalente en Azure/GCP. Si te vas, tirás
  supervisor_agent.py y lo corrés en un container propio (ECS, Cloud Run, K8s). Perdés:
  sesiones persistentes, observabilidad built-in, memory service, gateway.
  - Nova Pro — modelo propietario AWS. Fuera de AWS no existe. Reemplazo: Claude
  (Anthropic API directo), GPT-4, Llama (self-hosted).
  - Lambda Function URL + S3 hosting — trivial de migrar pero es AWS.
  - Cognito — cualquier OAuth2 provider lo reemplaza (Auth0, Keycloak).

  📊 Tabla de "¿cuánto cuesta portarlo?"

  ┌─────────────────────────────────────┬────────────────────────────────┐
  │             Componente              │ Tiempo para migrar a GCP/Azure │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Frontend                            │ 0 horas                        │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Backend FastAPI                     │ 1 hora                         │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Strands Agent (cambiar a Claude)    │ 2 horas                        │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Lambda tools → Cloud Functions      │ 4 horas                        │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ AgentCore → hacer tu propio runtime │ 20-40 horas                    │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Cognito → Auth0                     │ 4 horas                        │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ IAM roles → IAM equivalente         │ 8 horas                        │
  ├─────────────────────────────────────┼────────────────────────────────┤
  │ Total estimado                      │ ~1 semana de trabajo           │
  └─────────────────────────────────────┴────────────────────────────────┘

  ---
  💡 Cómo defenderlo en preguntas de la charla

  Pregunta típica: "¿Y si mañana AWS sube los precios de AgentCore?"

  ▎ "Buen punto. La arquitectura está 70% desacoplada: Strands, MCP y las tools son open
  ▎ source y portables. Lo que está atado es AgentCore como runtime — en 1 semana de
  ▎ trabajo reemplazás eso por ECS + Redis para sesiones. El vendor lock-in real está en
  ▎ Nova Pro como modelo, pero eso se cambia con una línea en Strands."

  Pregunta típica: "¿Por qué no usaste LangChain?"

  ▎ "Strands está hecho por AWS específicamente para Bedrock, con menos abstracciones y
  ▎ mejor integración con AgentCore. Para este caso de uso (4 tools, un supervisor) era
  ▎ más simple. LangChain sería mejor si necesitara multi-agent complejo o proveedores
  ▎ mixtos."

  Pregunta típica: "¿Es multi-tenant?"

  ▎ "Hoy no. Cognito está configurado pero el código no segrega por usuario real —
  ▎ user_id es mock. Para prod habría que: JWT por request, aislamiento de user_memory
  ▎ por tenant, rate limits."

  ---
  🎯 Los 3 conceptos clave para memorizar

  1. "Bedrock = 3 APIs: Runtime (modelos), AgentCore (agentes), AgentCore Control
  (CRUD)."
  2. "No hay API keys — IAM SigV4 maneja todo. Local: AWS_PROFILE. Prod: rol IAM
  asumido."
  3. "70% del stack es portable (Strands, MCP, tools, frontend). El 30% atado es
  AgentCore + Nova Pro."

  ¿Querés que arme un diagrama ASCII más detallado de los flujos de autenticación
  (IAM/SigV4) o que te haga un quiz de preguntas sorpresa para que practiques responder
  sin notas?

✻ Baked for 1m 20s