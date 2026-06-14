# CI/CD en Microsoft Fabric

> Repositorio de la charla presentada en el **Global Fabric Day 2026 – Alicante**  
> por Oliver Bernabeu

---

## 📋 Descripción

Este repositorio contiene todos los recursos necesarios para implementar un pipeline completo de **CI/CD en Microsoft Fabric** usando Azure DevOps y la librería `fabric-cicd`. Incluye el código de la pipeline, los scripts de despliegue, los elementos del workspace de Fabric y la presentación de la charla.

---

## 📁 Estructura del repositorio

```
├── deploy/
│   ├── pipelines/
│   │   └── deploy-pipeline.yml          # Pipeline de Azure DevOps
│   └── scripts/
│       ├── debug_parametrization.py     # Script de validación de parámetros
│       └── fabric_cicd_deployment.py    # Script principal de despliegue con fabric-cicd
│
├── slides/
│   └── GlobalFabricDay2026_CICD.pdf     # Presentación de la charla
│
└── src/
    └── workspaces/
        └── DEV_DEMO_CICD/               # Elementos del workspace de Fabric
            ├── 01_load_csv_to_delta.Notebook
            ├── 02_load_gold.Notebook
            ├── 03_orquestador.DataPipeline
            ├── lh_bronze.Lakehouse
            ├── lh_gold.Lakehouse
            ├── Sales Dataset.Report
            ├── Sales Dataset.SemanticModel
            ├── Sales Report.Report
            ├── vl_environment_variables.VariableLibrary
            └── parameter.yml            # Configuración de parámetros por entorno
```

---

## 🏗️ Arquitectura

El proyecto implementa una arquitectura **medallion** sobre Microsoft Fabric:

| Capa | Elemento | Descripción |
|------|----------|-------------|
| **Bronze** | `lh_bronze` + `01_load_csv_to_delta` | Ingesta de datos crudos desde CSV a Delta |
| **Gold** | `lh_gold` + `02_load_gold` | Transformación y modelado de datos |
| **Orquestación** | `03_orquestador` | Pipeline que coordina la ejecución end-to-end |
| **Semántica** | `Sales Dataset.SemanticModel` | Modelo semántico sobre la capa Gold |
| **Reporting** | `Sales Dataset.Report` / `Sales Report.Report` | Informes de Power BI |

---

## 🚀 Pipeline de CI/CD

El flujo de despliegue se basa en **Azure DevOps** + **[fabric-cicd](https://github.com/microsoft/fabric-cicd)**:

```
Git (DEV branch)  →  Azure DevOps Pipeline  →  fabric_cicd_deployment.py  →  Fabric Workspace (PROD)
```

### Pasos principales

1. **Trigger** – La pipeline se lanza al mergear a la rama de producción.
2. **Parametrización** – `parameter.yml` sustituye los valores específicos de entorno (endpoints, IDs de workspace, connection strings...).
3. **Validación** – `debug_parametrization.py` verifica que las sustituciones son correctas antes del despliegue.
4. **Despliegue** – `fabric_cicd_deployment.py` invoca `publish_all_items()` para publicar todos los elementos en el workspace destino.

### Configuración (`parameter.yml`)

El fichero `parameter.yml` contiene las sustituciones de parámetros entre entornos DEV y PROD. Ejemplo de estructura:

```yaml
find_replace:
  - find: "<DEV_SQL_ENDPOINT>"
    replace: "<PROD_SQL_ENDPOINT>"
    item_type: SemanticModel

  - find: "<DEV_WORKSPACE_ID>"
    replace: "<PROD_WORKSPACE_ID>"
```

---

## ⚙️ Requisitos previos

- **Azure DevOps** con un agente configurado (o Microsoft-hosted agent con acceso a Fabric)
- **Python 3.9+**
- **fabric-cicd** ≥ 1.1.0
  ```bash
  pip install fabric-cicd
  ```
- **Workspace Identity** habilitada en el workspace de Fabric destino
- Integración **Git** activa en el workspace DEV

---

## 🛠️ Uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/<nombre-repo>.git
cd <nombre-repo>
```


---

## 📊 Slides

La presentación completa de la charla está disponible en:

```
slides/GlobalFabricDay2026_CICD.pdf
```

---

## 🔗 Referencias

- [fabric-cicd – Microsoft GitHub](https://github.com/microsoft/fabric-cicd)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric)
- [Global Fabric Day 2026](https://globalfabricday.com)

---

## 📄 Licencia

Este repositorio es de carácter educativo y se comparte abiertamente como material de apoyo a la charla. Siéntete libre de adaptarlo a tus propios proyectos.