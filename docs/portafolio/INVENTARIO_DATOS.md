# Inventario de datos públicos de portafolios grandes (PF-001, Fase 0)

2026-10-21. Autor: `portafolio-replica`. Sin retornos, sin descargas de datasets, nada escrito en `data/`.
Método: prueba de acceso desde este entorno (curl HEAD por el proxy) + lectura de páginas oficiales de la SEC vía WebFetch. Lo marcado **[NO VERIFICADO]** no se pudo confirmar.

## 0. Acceso desde este entorno (prueba del 2026-10-21)

El proxy del entorno responde **403 en el CONNECT** (política de hosts permitidos) para TODOS los dominios probados. Ninguna descarga directa es posible hoy:

| Host probado | Resultado |
|---|---|
| www.sec.gov (páginas DERA 13F y N-PORT, zip 13F, full-index) | 403 proxy |
| data.sec.gov (submissions API) | 403 proxy |
| www.ishares.com (página y CSV de tenencias) | 403 proxy |
| www.ssga.com (SPY) | 403 proxy |
| farside.co.uk (flujos BTC; además no oficial) | 403 proxy |
| stooq.com, query1.finance.yahoo.com (precios; no oficiales) | 403 proxy |

Lo que sí se leyó: páginas SEC por WebFetch (herramienta aparte del proxy): `sec.gov/dera/data/form-13f` y `sec.gov/files/form_13f_readme.pdf`. `sec.gov/dera/data/form-nport` quedó bloqueada (permiso no respondido) y la nota de plazos N-PORT (shearman) redirige: **N-PORT no verificado en primera mano**.
Para descargar hace falta que el usuario habilite `www.sec.gov` y `data.sec.gov` en la política del proxy (más el emisor de ETF elegido). Además, la SEC exige un User-Agent identificado y máx. 10 solicitudes/seg [NO VERIFICADO hoy, regla pública conocida].

## 1. SEC DERA — Form 13F Data Sets

- URL: https://www.sec.gov/dera/data/form-13f (readme: https://sec.gov/files/form_13f_readme.pdf)
- Cobertura: 2013 T2 a agosto 2026 (página actualizada 2026-08-31).
- Frecuencia / empaque: 2013 T2–2023 T4 un zip por trimestre (`2023q4_form13f.zip`). **Desde 2024**: zips de 3 meses que terminan en feb/may/ago/nov (`01mar2024-31may2024`); el primero (ene–feb 2024) tiene 2 meses. Hay que mapear por FILING_DATE y PERIODOFREPORT, no por nombre de archivo.
- Fecha real de publicación: FILING_DATE (tabla SUBMISSION) por cada presentación; PERIODOFREPORT es la fecha del dato. Rezago legal máx. 45 días tras el cierre del trimestre; el rezago real se mide por filing. Lo presentado después de las 17:30 ET del último día hábil del trimestre de datos pasa al zip siguiente. El zip mismo se publica poco después de cada vencimiento: **el zip es posterior al FILING_DATE; usar FILING_DATE, no la fecha del zip**.
- Formato: TSV UTF-8 dentro de zip; tablas SUBMISSION, COVERPAGE, OTHERMANAGER(2), SIGNATURE, SUMMARYPAGE, INFOTABLE. Clave ACCESSION_NUMBER. Tipos incluidos: 13F-HR, 13F-HR/A, 13F-NT, 13F-NT/A.
- Costo: no indica licencia ni costo; es público y gratuito (dominio público de la SEC). Descarga desde este entorno: **INACCESIBLE (403 proxy)**.
- Riesgos:
  - Enmiendas: vienen con redundancias/discrepancias respecto de presentaciones previas; hay que tratar cada 13F-HR/A como un evento con su propio FILING_DATE (regla del borrador PF-001).
  - La SEC reprocesó todos los sets el 2024-03-12 y actualizó 2023 el 2024-01-09: **los zips actuales no son idénticos a lo que existía en la fecha original** (revisión silenciosa). Guardar checksum y fecha de bajada.
  - VALUE: en miles hasta 2022 y en dólares enteros desde 2023-01-03. Cambio de unidad, riesgo de error x1000.
  - Confidencialidad: hay campos (ISCONFIDENTIALOMITTED, DATEDENIEDEXPIRED, etc.); posiciones omitidas pueden aparecer luego vía enmienda.
  - Solo largos en acciones/opciones listadas en EE. UU.; sin cortos ni efectivo.
  - CUSIP (CHAR 9, FIGI opcional): sin tabla CUSIP-ticker oficial gratuita; mapear a precios es el punto débil. CUSIP cambian por fusiones/reestructuras.
  - La SEC no garantiza exactitud; puede haber errores de extracción.
  - Sesgo de supervivencia: el dato de tenencias incluye empresas muertas (bien), pero los precios gratuitos suelen no tenerlas (ver sección 5).

## 2. SEC EDGAR directo (índices y filings)

- URLs: https://www.sec.gov/Archives/edgar/full-index/ (form.idx por trimestre), https://data.sec.gov/submissions/CIK##########.json, filings 13F XML/texto.
- Cobertura: índices desde 1993; 13F en XML estructurado solo desde 2013 T2; antes texto libre (parseo propenso a error).
- Fecha real: el índice y submissions dan la fecha de presentación y el tipo (13F-HR, /A) -> sirve para auditar el FILING_DATE de DERA y detectar enmiendas.
- Formato: texto/JSON/XML. Gratis. **INACCESIBLE (403 proxy)**.
- Riesgos: pedido por fondo es lento (límite de tasa); 13F anteriores a 2013 no comparables con DERA.

## 3. SEC — Form N-PORT (fondos y ETF registrados)

- URL esperada: https://www.sec.gov/dera/data/form-nport **[NO VERIFICADO: página bloqueada]**.
- Cobertura según referencias: desde 2019 (sec-api.io indica "2019–presente", fuente no oficial); a confirmar.
- Frecuencia: tenencias mensuales presentadas; públicas solo las del último mes de cada trimestre fiscal, ~60 días después del cierre [NO VERIFICADO primera mano; coincide con el borrador].
- Formato esperado: zips trimestrales TSV [NO VERIFICADO]. Gratis. **Descarga: INACCESIBLE (403 proxy)**.
- Riesgos: solo fondos registrados (no hedge funds); rezago más largo que 13F; incluye bonos y derivados (más complejo de mapear); revisiones/enmiendas NPORT-P/A [NO VERIFICADO]; poca historia (~6,5 años).

## 4. Tenencias diarias de ETF (iShares, SPDR, etc.)

- URLs: página y CSV por producto en ishares.com / ssga.com (ej. IVV, SPY).
- Cobertura: solo el día actual; **no hay archivo histórico oficial gratuito** (coincide con el borrador). Sirve solo prospectivo (hay que bajarlo y archivarlo cada día con checksum).
- Fecha real: T+1 aprox.; la fecha "as of" viene dentro del archivo; el momento real de publicación solo se conoce si se archiva a diario.
- Formato: CSV/XLS con encabezado variable por emisor. Gratis en la web del emisor; términos de uso del sitio por revisar. **INACCESIBLE (403 proxy)**.
- Riesgos: sin historia = no hay prueba histórica; el formato cambia sin aviso; raspado de web puede violar términos [revisar].

## 5. Flujos / tenencias de ETF spot de BTC

- Fuentes oficiales: sitio de cada emisor (IBIT/BlackRock, FBTC/Fidelity, etc.): BTC en custodia, acciones, NAV diarios; flujo = diferencia de acciones x NAV (derivado, no publicado como flujo). También 10-K/10-Q/8-K en EDGAR (trimestral, inaccesibles hoy).
- Cobertura: desde 2024-01-11 (~2,8 años). Frecuencia diaria, T+1.
- Agregadores de flujos (Farside, etc.): **no oficiales, quedan fuera por regla del rol**; además 403.
- Riesgos: el flujo derivado mezcla creaciones/rescates con cambios de precio; fecha "as of" vs publicación; historia insuficiente para prueba confirmatoria (MDE 1,68 en el borrador); solo uso descriptivo prospectivo.
- Descarga: **INACCESIBLE (403 proxy)**.

## 6. Precios (necesarios para cualquier réplica; NO se descargó nada)

- Fuentes gratuitas probadas (Stooq, Yahoo): no oficiales y **403 proxy**. CRSP/Compustat/Norgate: de pago, fuera de alcance.
- Riesgo central abierto (punto 3 del borrador): fuentes gratuitas suelen no tener empresas deslistadas ni ajustes correctos por fusiones -> sesgo de supervivencia al alza. Sin una fuente oficial/gratuita con deslistadas, el desconfiado debería exigir declararlo o descartar la réplica por precios.

## 7. Cobertura y huecos para Fase 0

| Dato | Estado hoy |
|---|---|
| 13F: nº de fondos por trimestre, % con FILING_DATE, enmiendas, huecos | **No contable**: no se pudo bajar nada. Pendiente de acceso |
| N-PORT | Sin verificar primera mano |
| ETF tenencias diarias | Sin historia; solo prospectivo |
| ETF BTC | ~2,8 años; solo descriptivo |
| Precios con deslistadas | Sin fuente gratuita verificada |

## 8. Qué se necesita para cerrar el inventario

1. Habilitar en el proxy: `www.sec.gov`, `data.sec.gov` (decisión del usuario/entorno; no la puedo cambiar yo).
2. Con eso: bajar SOLO tablas SUBMISSION/COVERPAGE de unos pocos zips para contar fondos, enmiendas y rezago real (sin INFOTABLE, sin precios), guardando checksum en la carpeta que indique el jefe.
3. Decidir con el jefe-riesgo/desconfiado qué hacer con el punto de precios de deslistadas.
