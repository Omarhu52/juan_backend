from fastapi import FastAPI, Depends, HTTPException, status, File,Form
from fastapi.responses import Response,RedirectResponse
from sqlalchemy.orm import Session
from models import Base, Usuario, Plan 
import models 
import schemas
import crud
from schemas import LoginData
from database import SessionLocal, engine
import uvicorn
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageTemplate,Frame
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib.units import inch
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List 
import random
from datetime import datetime, timedelta


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(login_data: LoginData, db: Session = Depends(get_db)):
    nombre = login_data.nombre
    contrasena = login_data.contrasena
    user = crud.get_usuario_by_nombre(db, nombre=nombre)
    print(nombre+" g")
    print(contrasena)
    print(user.id_usuario)
 
    user = crud.get_usuario_by_nombre(db, nombre=nombre)
    if not user or user.contrasena != contrasena:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos"
        )
    
    response_data = {
        "message": "",
        "id_usuario": user.id_usuario,
        "nombre": user.nombre
    }

    if user.rol == "Admin":
        response_data["message"] = "Bienvenido al panel de administración"
    elif user.rol == "Usuario":
        response_data["message"] = "Bienvenido al panel de usuario"
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rol no autorizado"
        )
    
    return response_data

@app.get("/admin_dashboard")
def admin_dashboard():
    return {"message": "Bienvenido al panel de administración"}

@app.get("/user_dashboard")
def user_dashboard():
    return {"message": "Bienvenido al panel de usuario"}

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.create_usuario(db=db, usuario=usuario)

@app.get("/usuarios/read/{cedula}", response_model=schemas.Usuario)
def read_usuario_cedula(cedula: int, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario_cedula(db=db, usuario_id=cedula)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return db_usuario

@app.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario(db=db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario not found")
    return db_usuario

@app.put("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def update_usuario(usuario_id: int, usuario: schemas.UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = crud.update_usuario(db=db, usuario_id=usuario_id, usuario=usuario)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return db_usuario

@app.delete("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def delete_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return crud.delete_usuario(db=db, usuario_id=usuario_id)


@app.post("/planes/", response_model=schemas.Plan)
def create_plan(plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.id_usuario == plan.id_usuario).first()
    if not usuario_existente:
        raise HTTPException(status_code=400, detail="El usuario especificado no existe")
    return crud.create_plan(db=db, plan=plan)

@app.get("/planes/{plan_id}", response_model=schemas.Plan)
def read_plan(plan_id: int, db: Session = Depends(get_db)):
    db_plan = crud.get_plan(db=db, plan_id=plan_id)
    if db_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    return db_plan

@app.put("/planes/{plan_id}", response_model=schemas.Plan)
def update_plan(plan_id: int, plan: schemas.PlanCreate, db: Session = Depends(get_db)):
    return crud.update_plan(db=db, plan_id=plan_id, plan=plan)

@app.delete("/planes/{plan_id}", response_model=schemas.Plan)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    return crud.delete_plan(db=db, plan_id=plan_id)


@app.get("/planes/usuario/{id_usuario}", response_model=List[schemas.Plan])
def get_planes_by_usuario_id(id_usuario: int, db: Session = Depends(get_db)):
    planes = crud.get_planes_by_usuario_id(db, id_usuario=id_usuario)
    if not planes:
        raise HTTPException(status_code=404, detail="No se encontraron planes para este usuario")
    return planes

def add_watermark(canvas, doc):
    canvas.saveState()
    watermark_path = "icono1.png"  
    if os.path.exists(watermark_path):
        watermark = Image(watermark_path, width=400, height=400)
        x = (letter[0] - 400) / 2
        y = (letter[1] - 400) / 2
        watermark.drawOn(canvas, x, y)
    canvas.restoreState()


def generar_factura(usuario_id: int, db: Session):
    db_usuario = crud.get_usuario(db=db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    db_plan = db.query(crud.Plan).filter(crud.Plan.id_usuario == usuario_id).first()
    if db_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan no encontrado")

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)

    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='watermark', frames=frame, onPage=add_watermark)
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        name="Title",
        parent=styles["Title"],
        fontSize=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#00AEEF"),
        spaceAfter=20,
        fontName='Helvetica-Bold' 
    )
    
    style_normal = ParagraphStyle(
        name="Normal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        leading=12,
    )
    style_bold = ParagraphStyle(
        name="Bold",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        leading=12,
        spaceAfter=14,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    style_right = ParagraphStyle(
        name="Right",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.black,
        leading=12,
        alignment=TA_RIGHT
    )
    style_summary_title = ParagraphStyle(
        name="SummaryTitle",
        parent=styles["Title"],
        fontSize=14,
        alignment=TA_LEFT,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )

    contenido = []
    image_path = "icono.png"  
    if os.path.exists(image_path):
        imagen = Image(image_path, width=100, height=50)
        contenido.append(imagen)
    
    contenido.append(Spacer(1, 20))
    
    header_table_data = [
        [
            Paragraph("Factura del servico de Telefonía e Internet ", style_title)
        ]
    ]
    header_table = Table(header_table_data, colWidths=[500])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'MIDDLE')
    ]))
    contenido.append(header_table)
    contenido.append(Spacer(1, 50))
    numero_factura = random.randint(20, 100)
    mes_actual = datetime.now()
    mes_actual1=mes_actual.strftime("%B")
    mes_anterior = mes_actual + timedelta(days=30)  
    nombre_mes_anterior = mes_anterior.strftime("%B")
    fecha_actual = datetime.now()
    client_info_data = [
        [Paragraph("Cliente", style_bold), f"{db_usuario.nombre}"],
        [Paragraph("Dirección", style_bold), db_usuario.direccion],
        [Paragraph("Nit ó Cédula", style_bold), db_usuario.cedula],
        [Paragraph("Teléfono", style_bold), db_usuario.telefono],
        [Paragraph("Fecha de expedición", style_bold), fecha_actual.strftime("%Y-%m-%d")],
        [Paragraph("Factura de venta No", style_bold), f"{numero_factura}"]
    ]
    client_info_table = Table(client_info_data, colWidths=[150, 250])
    client_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    contenido.append(client_info_table)
    contenido.append(Spacer(1, 12))

    
    invoice_details_data = [
        ["Factura Mes", mes_actual1, "Número para pagos", "8080365493515621"],
        ["Fecha Entrega", fecha_actual.strftime("%Y-%m-%d"), "Fecha límite de Pago", f"{db_usuario.fecha_de_corte}"],
        ["Próxima Factura", nombre_mes_anterior, "TOTAL A PAGAR", f"${db_plan.precio:.2f}"]
    ]
    invoice_details_table = Table(invoice_details_data, colWidths=[150, 100, 150, 100])
    invoice_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    contenido.append(invoice_details_table)
    contenido.append(Spacer(1, 20))

    # Account Summary Title
    contenido.append(Paragraph("RESUMEN DE TU CUENTA", style_summary_title))
    contenido.append(Spacer(1, 12))

    # Account Summary Table
    account_summary_data = [
      ["Servicio", "Mes Anterior", "Facturas Pendientes", "Mes Actual", "Total a Pagar"],
      [db_plan.tipo_de_plan, f"${db_plan.precio:.2f}", "$0.00", f"${db_plan.precio:.2f}", f"${db_plan.precio:.2f}"]
    ]
    account_summary_table = Table(account_summary_data, colWidths=[100, 100, 100, 100, 100])
    account_summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    contenido.append(account_summary_table)
    contenido.append(Spacer(1, 20))

    total = db_plan.precio
    monto_base = total / 1.19  
    impuesto = total - monto_base  

    totals_table = Table([
        ["", "Monto Base", "Valor Impuesto"],
        ["IVA 19%", f"${monto_base:.2f}", f"${impuesto:.2f}"],
        ["Total", "", f"${total:.2f}"]
    ], colWidths=[200, 140, 140])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.white),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    contenido.append(totals_table)


    contenido.append(Paragraph("Estimado Cliente, pague oportunamente y evite la suspensión del servicio, cobro de reconexión por producto e intereses de mora. El incumplimiento en los pagos genera reportes a Centrales de Riesgo como moroso. Si ya realizó el pago, haga caso omiso.", style_normal))
    contenido.append(Spacer(1, 20))

    barcode_path = "barras.png"  
    if os.path.exists(barcode_path):
      barcode_image = Image(barcode_path, width=200, height=50)  
      barcode_image.hAlign = 'CENTER'
      contenido.append(barcode_image)
      contenido.append(Spacer(1, 20))
    footer_data = [
        ["", "", "", "", "Página 1 de 1"]
    ]
    footer_table = Table(footer_data, colWidths=[100, 100, 100, 100, 100])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    contenido.append(footer_table)

    doc.build(contenido)
    pdf_bytes = pdf_buffer.getvalue()
    
    return pdf_bytes

@app.get("/factura/{usuario_id}")
def generar_factura_endpoint(usuario_id: int, db: Session = Depends(get_db)):
    pdf_bytes = generar_factura(usuario_id, db)
    
    response = Response(content=pdf_bytes, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=factura_usuario_{usuario_id}.pdf"
    return response

origins = [
    "http://127.0.0.1:5000"  # URL de tu frontend Flask
    #"https://tufrontend.com",  # Si tienes un dominio de producción para el frontend
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
