from fastapi import FastAPI, HTTPException, Depends
from database import get_db_connection
from schemas import ProductoNuevo, UsuarioRegistro, UsuarioLogin, NuevaCompra
from security import crear_token_acceso, verificar_token
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def prueba_servidor():
    return {"mensaje: Servidor funcionando"}

#creamos las rutas endpoints para los productos

# 1 crear POST, que agrega un producto a la base de datos

@app.post("/productos/")
def crear_producto(producto: ProductoNuevo, token_valido: dict = Depends(verificar_token)):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error al conectar a la base de datos")

    cursor = conexion.cursor()
    #escribimos el comando de mysql, usando %s como comodines por seguridad 
    sql = "INSERT INTO Productos (nombre, descripcion, precio, stock) VALUES (%s, %s, %s, %s)"
    valores = (producto.nombre, producto.descripcion, producto.precio, producto.stock)

    cursor.execute(sql, valores)
    conexion.commit() #confirmamos el guardado definitivo

    nuevo_id = cursor.lastrowid # obtenemos el id que mysql le asigno automaticamente 

    cursor.close()
    conexion.close()

    return {"mensaje": "Producto creado con exito", "id_producto": nuevo_id}


# 2 ahora creamos get (LEER) para traer todos los productos del catalogo

@app.get("/productos/")
def obtener_productos():
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")


    #dictionary true, va a hacer que los datos salgan en formato clave-valor
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Productos")
    productos = cursor.fetchall() # fetchall significa traer todo

    cursor.close()
    conexion.close()

    return productos


# 3. ACTUALIZAR (PUT) - Modifica un producto que ya existe
@app.put("/productos/{id_producto}")
def actualizar_producto(id_producto: int, producto: ProductoNuevo, token_valido: dict = Depends(verificar_token)):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión")
    
    cursor = conexion.cursor()
    # Escribimos el comando UPDATE apuntando a un ID específico
    sql = "UPDATE Productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s WHERE id_producto=%s"
    valores = (producto.nombre, producto.descripcion, producto.precio, producto.stock, id_producto)
    
    cursor.execute(sql, valores)
    conexion.commit()
    
    # rowcount nos dice cuántas filas se modificaron
    filas_afectadas = cursor.rowcount 
    cursor.close()
    conexion.close()
    
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Error: Producto no encontrado")
        
    return {"mensaje": "Producto actualizado con éxito"}

# 4. BORRAR (DELETE) - Elimina un producto del catálogo
@app.delete("/productos/{id_producto}")
def borrar_producto(id_producto: int, token_valido: dict = Depends(verificar_token)):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexión")
    
    cursor = conexion.cursor()
    # Ejecutamos el comando DELETE.
    sql = "DELETE FROM Productos WHERE id_producto=%s"
    
    cursor.execute(sql, (id_producto,))
    conexion.commit()
    
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()
    
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Error: Producto no encontrado")
        
    return {"mensaje": "Producto eliminado con éxito"}



# RUTAS para USUARIOS Y SEGURIDAD (JWT)

# 5 aca vamos a registrar un usuario que se va a guardar en la base de datos

@app.post("/registro")
def registrar_usuario(usuario: UsuarioRegistro):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor()
    sql = "INSERT INTO Usuarios (nombre, email, contrasena) VALUES (%s, %s, %s)"
    valores = (usuario.nombre, usuario.email, usuario.contrasena)

    try:
        cursor.execute(sql, valores)
        conexion.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al registrar")
    finally:
        cursor.close()
        conexion.close()

    return {"Mensaje": "Usuario registrado con exito"}


# 6 aca vamos a hacer el login, que verifica los datos y entrega el token JWT

@app.post("/login/")
def iniciar_sesion(usuario: UsuarioLogin):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor(dictionary=True)
    #buscamos si existe alguien con ese mail y contrasena exacta
    sql = "SELECT * FROM Usuarios WHERE email=%s AND contrasena=%s"

    cursor.execute(sql,(usuario.email, usuario.contrasena))
    usuario_db = cursor.fetchone() # va a traer un solo resultado o none si no existe

    cursor.close()
    conexion.close()

    #en el caso de que no lo haya encontrado tiramos ese error
    if not usuario_db :
        raise HTTPException(status_code=401, detail="Email o Contrasena incorrectos")


    #en el caso de que si haya llegado hasta el final se le entrega el token
    token = crear_token_acceso({"email": usuario_db["email"]})

    return {"Mensaje": "Login exitoso", "token": token}


# ahora vamos a crear la parte de registrar compra que requiere estar logeado

@app.post("/comprar/")
def registrar_compra(compra: NuevaCompra, token_valido: dict = Depends(verificar_token)):
    conexion = get_db_connection()
    if not conexion:
        raise HTTPException(status_code=500, detail="Error de conexion")

    cursor = conexion.cursor()

    try:
        # en lugar de INSERT vamos a llamar al callproc, que seria el procedimiento almacenado
        cursor.callproc('RegistrarCompra', (compra.id_usuario, compra.id_producto, compra.cantidad))
        conexion.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar la compra: {e} ")
    finally:
        cursor.close()
        conexion.close()

    return{"Mensaje": "Compra registrada con exito!"}