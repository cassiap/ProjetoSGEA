# SGEA — Sistema de Gestão de Eventos Acadêmicos

Estrutura **idêntica ao exemplo do professor** (1 app, `forms.py`, `views.py` funcionais, `urls.py`, `templates/`, `static/`).

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

## Fluxo
- Cadastro/Login de usuário e criação automática de perfil
- Organizador: CRUD de eventos
- Aluno/Professor: inscrição em eventos
- Emissão de certificado por inscrição (geração de código)

2025-10-08 12:21:14
