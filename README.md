# KLayout Lithography Toolbox

Este repositório contém a biblioteca de PCells **NIST Lithography & Nanophotonics** e **NIST MEMS & NEMS** baseada no *CNST Nanolithography Toolbox*, portada e otimizada para Python usando a API nativa do KLayout (`pya`).

## Funcionalidades
*   **53 PCells verificadas** e implementadas (incluindo Arrays Retangulares/Hexagonais/Polares, Verniers, Fractais, Grades de Acoplamento, Guias de Onda, Mola Circular, Atuador Térmico, Bolômetro, Flexuras Ancoradas, etc.).
*   Totalmente compatível com o KLayout (carregamento automático na inicialização).
*   Portável e fácil de distribuir.

## Instalação

### Linux / macOS (Automatizado)
Você pode instalar facilmente usando o script de instalação incluído:

1.  Abra o terminal no diretório do projeto clonado.
2.  Execute o script:
    ```bash
    chmod +x install.sh
    ./install.sh
    ```
3.  Abra ou reinicie o KLayout. As bibliotecas `NIST_LithoToolbox` e `NIST_MEMS_NEMS` estarão disponíveis para uso na paleta de PCells.

### Windows / Outros (Manual)
1.  Abra o diretório do usuário do KLayout (geralmente `C:\Users\<SeuUsuario>\KLayout` ou `%APPDATA%\KLayout`).
2.  Crie uma pasta chamada `salt` se ela não existir.
3.  Crie uma pasta chamada `klayout-lithography-toolbox` dentro de `salt`.
4.  Copie o arquivo `grain.xml` e as pastas `pymacros` e `python` para dentro dela.
5.  Abra ou reinicie o KLayout.

## Testando os PCells localmente
Você pode validar que todas as 53 PCells estão compilando e gerando geometria sem erros executando o script de teste incluído (em modo batch):
```bash
klayout -b -r python/test_all_pcells.py
```

## Estrutura do Repositório
*   `grain.xml`: Metadados do pacote KLayout.
*   `install.sh`: Script de instalação rápida para sistemas baseados em Unix.
*   `pymacros/`: Script macro autorun (`register_library.lym`) que inicializa as bibliotecas ao iniciar o KLayout.
*   `python/`: Implementação das PCells e helpers de desenho (`cnst_extended.py`, `cnst_extended_pcells.py`, `register_library.py`).
*   `python/test_all_pcells.py`: Script de validação.
