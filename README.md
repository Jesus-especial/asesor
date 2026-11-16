# Bot de atención para utilería escénica

Proyecto independiente de prueba: Telegram + Venice AI + FAQ editable + búsqueda semántica local. No depende de la plantilla descargada. Está configurado para responder sobre utilería destinada a videos musicales y contenido audiovisual. El producto no es moneda ni medio de pago.

## Antes de usarlo

La FAQ contiene las respuestas y precios que proporcionaste para el negocio: paquetes 10, 18, 25 y 32, y envío nacional por Servientrega por $6 adicional. Los contenidos de paquetes se expresan como cantidad de piezas, sin denominaciones. Revisa los datos antes de atender clientes. No presentes el producto como válido para compras o pagos reales. No pongas claves ni datos personales en el archivo.

## Preparación

1. Instala Python 3.11 o posterior.
2. Abre una terminal en esta carpeta y crea un entorno:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. Copia `.env.example` a `.env`.
4. Completa `TG_TOKEN`, `VENICE_API_KEY` y `VENICE_MODEL`. El token se obtiene al crear un bot de Telegram; el nombre del modelo debe ser uno habilitado en tu cuenta de Venice.
5. Ejecuta `python main.py` una vez. Abre la conversación privada con el bot desde la cuenta de Telegram Business que conectarás, envíale `/id` y copia el número que devuelve.
6. Detén el bot, completa `ADMIN_CHAT_ID` en `.env` con ese número y vuelve a iniciar. Se usa para identificar tus propios mensajes en los chats Business y enviarte alertas.
7. En Telegram, conecta el bot a la cuenta desde los ajustes de Telegram Business y habilita los permisos para leer y responder mensajes. Para borrar el comando enviado desde tu cuenta, la conexión necesita `can_delete_all_messages`. Telegram puede no borrar el comando; el bot lo intenta y registra/avisa si falla, así que no se garantiza que el cliente no lo vea.
8. La primera ejecución descargará el modelo de embeddings multilingüe para usarlo localmente.

## Editar preguntas y respuestas

Abre `faq.csv` directamente con Excel. Está guardado en UTF-8 y separado por punto y coma para que Excel en español muestre las columnas y los acentos correctamente. Cada fila es un tema:

- `id`: identificador único, sin repetir.
- `categoria`: tema, por ejemplo `Materiales`, `Precios` o `Entrega`.
- `preguntas`: ejemplos alternativos separados por `|`.
- `respuesta`: información aprobada que el bot puede usar.

Puedes agregar, editar o eliminar filas mientras el bot está encendido. Los cambios se detectan automáticamente en la siguiente consulta. Guarda el archivo como CSV UTF-8 y conserva el separador punto y coma. Haz una copia de respaldo antes de cambios importantes.

Las filas principales originales se envían siempre al modelo: `negocio`, `precios`, `paquete_1` a `paquete_4`, `materiales`, `calidad`, `envios`, `entrega_ecuador_horarios`, `envios_internacionales`, `discrecion_envio`, `contra_entrega`, `objecion_contra_entrega`, `entrega_personal`, `video_confianza`, `pagos`, `menor_precio`, `prestamo`, `venezuela`, `pagos_internacionales`, `uso_utileria` y `riesgos_utileria`. Las dos últimas son respuestas distintas: una sobre dónde usar el material y otra sobre riesgos de uso. Conserva sus IDs si quieres que se envíen siempre y que las reglas que los mencionan sigan correspondiendo. Si borras o renombras una fila principal, esa fila deja de enviarse automáticamente; las filas nuevas y las respuestas aprendidas se buscan semánticamente. En ese caso revisa también las reglas del prompt.

## Explicarle al bot qué hace el negocio

Edita `system_prompt.txt` para cambiar el nombre y perfil del negocio, el objetivo, el tono y sus reglas de atención. El bot vuelve a leer ese archivo al generar cada respuesta, así que los cambios no requieren modificar Python ni reiniciar el proceso. Usa `faq.csv` para los datos concretos que cambian o deben responderse con exactitud (precios, materiales, plazos, opciones y políticas confirmadas).

El prompt también contiene ejemplos de mensajes para distinguir las situaciones de atención. Las respuestas principales siguen en la FAQ: los ejemplos del prompt muestran cuándo usar cada fila y no sustituyen su contenido editable.

## Telegram Business, alertas e intervención manual

El bot atiende mensajes de la conexión Telegram Business; los mensajes normales enviados a la conversación privada del bot no se procesan como consultas de clientes. Responde usando esa conexión Business. El administrador se reconoce mediante `ADMIN_CHAT_ID`, que debe ser el ID de tu propia cuenta.

Los mensajes seguidos de un cliente se agrupan durante 5 segundos de silencio, con un máximo de 15 segundos desde el primer mensaje. Luego el bot muestra “escribiendo…” y espera entre 3 y 6 segundos antes de responder, como en la plantilla.

En el chat del cliente, desde tu cuenta Business:

- `/pause` pausa el bot para esa conversación e intenta borrar el comando.
- `/play` reactiva el bot e intenta borrar el comando.
- Cualquier otro mensaje de texto que escribas manualmente pausa el bot en esa conversación y se agrega al historial como respuesta tuya.
- Después de responder manualmente al cliente, `/faq_save` guarda, solo cuando tú lo ordenas, la última pregunta del cliente y tu respuesta exacta. No inventa variaciones. La entrada queda en `data/learned_faq.json`, separada de `faq.csv`, y el buscador la incorpora automáticamente para intentar encontrar preguntas parecidas; al depender de búsqueda semántica, no garantiza reconocer todas las formas de preguntar.

En el chat privado del bot, desde la cuenta configurada como administradora:

- `/faq_list` muestra las respuestas aprobadas y sus IDs.
- `/faq_off aprendida_0001` desactiva una respuesta sin borrarla.
- `/faq_on aprendida_0001` la vuelve a activar.
- `/faq_delete aprendida_0001` la elimina definitivamente.

Estos comandos de administración solo aceptan mensajes de la cuenta indicada en `ADMIN_CHAT_ID`. El ID se confirma por privado después de guardar con `/faq_save`. Si Telegram no puede borrar el comando del chat Business, puede que el cliente lo vea; el bot avisa si ocurre.

El asistente recibe la fecha y hora actuales de Ecuador en cada consulta. Conserva hasta 30 mensajes de historial por chat mientras el proceso está activo. Para evitar consultas concurrentes al modelo, procesa una consulta a la vez en todo el bot; si llegan preguntas de distintos clientes al mismo tiempo, esperan su turno.

La contraentrega y la confianza por video son temas separados. Si solo preguntan por contraentrega, el bot usa la respuesta de esa FAQ. Si dicen que no compran sin contraentrega, usa `objecion_contra_entrega`; esa objeción por sí sola no activa video ni alerta. La afirmación de esa respuesta sobre quiénes pueden usar contraentrega debe verificarse para cada país y transportista. Si además hay desconfianza sobre el negocio o el pedido, se aplica la regla de video. Las dudas sobre si el pedido llegará, si el negocio cumplirá o si es de confianza, y los relatos de estafas cometidas por terceros, usan `video_confianza`, añaden `[[ALERTA:VIDEO]] [[PAUSAR]]`, generan una alerta y pausan ese chat. Los insultos o acusaciones directas de estafa contra el negocio usan silencio y alerta de hostilidad. La grabación con el nombre y la fecha actual, y el envío del video, quedan a cargo de la persona administradora.

La hora de corte de Servientrega (17:00, hora de Ecuador) y el calendario de despacho/llegada se aplican solo cuando el cliente confirmó que está en Ecuador. El negocio indicó que un pago el jueves después de las 17:00 se despacha el viernes y llega el sábado; verifica esta condición con el transportista. Si el país aún no se conoce, se indica la información general disponible y se pregunta la ciudad o el país sin calcular una fecha exacta. Para un destino internacional confirmado, el prompt indica responder con el plazo general de 4 a 5 días laborables, sin calcular ni prometer una fecha u hora exactas. Verifica los plazos con el transportista.

La respuesta de pagos conserva los métodos ya aprobados. Sin país indicado, presenta los métodos generales con su aplicabilidad y pregunta cuál le sirve. Para Ecuador explica que clientes de otros bancos y de DeUna o PeiGo pueden transferir directamente a Banco Guayaquil, con acreditación en máximo 20 minutos; también aclara que no se reciben pagos por PayPal ni Zelle. El bot nunca comparte datos bancarios o credenciales de pago.

Las alertas privadas incluyen tipo de evento, nombre/usuario, ID, enlace al chat y el mensaje que requiere atención. Se envían para intención de compra, fotos/muestras, video de confianza, consulta sin respuesta, hostilidad, archivos/medios y errores del bot. Si ocurre un error interno, el bot no envía respuesta al cliente: pausa la atención automática y te alerta para revisar. El bot puede informar métodos aceptados y pedir el país para confirmar cuáles aplican, pero no entrega números de cuenta, titular ni direcciones de billetera; tampoco pide cédula, teléfono, dirección o datos de envío. Las preguntas sobre pruebas de autenticidad reciben una respuesta general de que el producto es utilería no válida para pagos, sin detalles de seguridad monetaria. Las pausas automáticas se activan al derivar una consulta, recibir medios o detectar una situación para atención humana. Las alertas te indican que respondas directamente al cliente desde Telegram Business. Los estados de pausa se guardan por conexión Business y chat en `data/paused_chats.json`; persisten al reiniciar.

Si el modelo responde solo con la frase de compra «Ya le ayudo un momento por favor» pero omite uno o ambos marcadores, el bot registra una advertencia y activa la alerta de compra y la pausa. Esta comprobación solo cubre esa frase (con o sin punto o exclamación); no garantiza detectar respuestas redactadas de otra manera. La entrega de la alerta también depende de que `ADMIN_CHAT_ID` esté configurado y Telegram acepte el mensaje.

El borrado del comando requiere `can_delete_all_messages` en la conexión Business y que Telegram acepte la solicitud. Puede fallar o no completarse antes de que el cliente lo vea; si falla, el bot lo registra y trata de avisarte por privado.

Para borrar mensajes enviados desde tu cuenta Business, concede al bot el permiso `can_delete_all_messages` en la conexión.

El saludo inicial usa la hora de Ecuador: buenos días de 05:00 a 11:59, buenas tardes de 12:00 a 18:59 y buenas noches de 19:00 a 04:59.

La FAQ incluye un ejemplo de envíos por Servientrega dentro de Ecuador y el envío internacional que indicaste. Revisa las condiciones y confirma que aplican a cada destino antes de ofrecerlas. La respuesta sobre empaque se refiere solo a empaque exterior neutro: no se oculta ni se declara falsamente el contenido y se deben seguir las normas del transportista y aduana.

La IA recibe siempre las filas principales indicadas arriba, más hasta cuatro respuestas adicionales recuperadas por búsqueda semántica, incluidas las aprendidas activas. No se duplican las filas principales recuperadas. Si una respuesta aprendida contradice una fila principal, revisa y actualiza la FAQ para evitar datos incompatibles; el modelo recibe ambas cuando la aprendida coincide y puede confundirse. Si no encuentra respaldo, se le instruye no inventar y derivar la consulta. Ajusta `MAX_COSINE_DISTANCE` en `.env` con consultas de prueba: un valor más bajo es más estricto. La distancia no es un porcentaje de confianza. Recibir los datos no garantiza que el modelo los interprete, copie literalmente o active alertas correctamente; prueba conversaciones reales.

## Pruebas

```powershell
python -m unittest discover -s tests
```

El historial reciente (hasta 30 mensajes por chat) se conserva en memoria mientras el proceso está activo y se pierde al reiniciarlo. La FAQ y sus vectores se guardan en `data/`; esa carpeta no debe borrarse si quieres conservar la base local. Para alojar el bot en línea después, necesitará almacenamiento persistente para esa carpeta o una base de datos equivalente.
