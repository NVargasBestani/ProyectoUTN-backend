from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta, timezone

#en un proyecto real esto se deberia ocultar, pero como es un tp lo dejamos aca

SECRET_KEY = "mi_clave_secreta_para_el_tp"
ALGORITHM = "HS256"

#con esto le vamos a decir a fastAPI que active el boton de autorize(candado) en la pagina web
revisor_tokens = HTTPBearer()

def crear_token_acceso(datos: dict):
    datos_a_codificar = datos.copy()

    #configuramos para que la sesion dure 30min
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=30)
    datos_a_codificar.update({"exp": expiracion})

    #creamos el token con la clave secreta
    token = jwt.encode(datos_a_codificar, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verificar_token(credenciales: HTTPAuthorizationCredentials = Security(revisor_tokens)):
    token = credenciales.credentials
    
    # ESPÍA: Esto va a imprimir en la terminal de Python exactamente lo que llega
    print(f"🕵️ TOKEN RECIBIDO DESDE REACT: {token}") 
    
    try:
        #esto va a intentar desencriptar el token con nuestra clave secreta
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload #si es valido sigue
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token vencido. Volve a iniciar sesion")
    except jwt.InvalidTokenError: # <--- BUG CORREGIDO (ahora dice InvalidTokenError)
        raise HTTPException(status_code=401, detail="Token invalido o falso")