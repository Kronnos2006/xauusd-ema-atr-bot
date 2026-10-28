# Kronnos — Verificador RFC3161 sin tokens IA
Uso: python3 tools/atlas_verificador_evidencias.py --data hipotesis.json --tsr sello.tsr --ca-file raiz_tsa.pem --event-utc 2026-11-01T00:00:00Z

Se usa openssl ts -verify para comprobar hash/firma/cadena del token RFC3161 y openssl ts -reply -text para leer genTime; se exige genTime previo al evento. La CA debe ser FIJADA y auditada independientemente, no una raíz elegida por quien fabricó el sello.

El código jamás habilita promoción. No obtiene sellos, no acredita custodia realmente independiente, no comprueba revocación, no demuestra censo exhaustivo ni valida DSR. Las pruebas CI negativas mock no sustituyen un ensayo positivo de RFC3161 de extremo a extremo con autoridad externa. No alterar ATLAS PR42.
