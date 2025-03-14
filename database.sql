USE [ACERONET]
GO
/****** Object:  Table [dbo].[planes]    Script Date: 12/03/2025 09:11:22 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[planes](
	[id_plan] [int] IDENTITY(1,1) NOT NULL,
	[tipo_de_plan] [varchar](max) NOT NULL,
	[precio] [int] NOT NULL,
	[megas] [varchar](max) NOT NULL,
	[tiempo_de_contrato] [varchar](max) NOT NULL,
	[numero_de_routes] [int] NOT NULL,
	[numero_de_decodificadores] [int] NOT NULL,
	[id_usuario] [int] NULL,
PRIMARY KEY CLUSTERED 
(
	[id_plan] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[usuarios]    Script Date: 12/03/2025 09:11:22 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[usuarios](
	[id_usuario] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](max) NOT NULL,
	[contrasena] [varchar](max) NOT NULL,
	[cedula] [bigint] NULL,
	[direccion] [varchar](max) NOT NULL,
	[correo] [varchar](max) NOT NULL,
	[telefono] [bigint] NULL,
	[ciudad] [varchar](max) NOT NULL,
	[departamento] [varchar](max) NOT NULL,
	[ubicacion_geografica] [varchar](max) NOT NULL,
	[estado] [varchar](max) NOT NULL,
	[fecha_de_corte] [varchar](max) NOT NULL,
	[rol] [varchar](max) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[id_usuario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
ALTER TABLE [dbo].[planes]  WITH CHECK ADD FOREIGN KEY([id_usuario])
REFERENCES [dbo].[usuarios] ([id_usuario])
GO
