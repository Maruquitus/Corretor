## Corretor de Gabaritos ✔️

Este é um sistema desenvolvido para reconhecimento e avaliação automática de questões e alternativas em folhas de respostas, utilizando visão computacional. O código está estruturado para capturar vídeo da webcam, detectar questões e alternativas, reconhecer respostas marcadas e compará-las com um gabarito predefinido.

### Requisitos do Sistema

- Python 3.x
- Bibliotecas: `cv2`, `time`, `inference`, `os`
- Nvidia CUDA e CUDNN

### Como usar
1. Clone o repositório ou faça o download dos arquivos.
2. Adicione uma chave de api do Roboflow em um arquivo .env como `ROBOFLOW_API_KEY`
3. Certifique-se de ter os requisitos instalados.
4. Execute o script Python.
5. Aponte a câmera da webcam para a folha de respostas.
6. Aguarde o sistema processar e reconhecer as questões e alternativas.
7. As respostas corretas serão comparadas com o gabarito e exibidas na tela.
8. Para sair do programa, pressione a tecla "q".

### Configurações

- **GABARITO:** O gabarito das questões é definido pela variável `GABARITO`.
- **Limiar de Interseção:** O valor de limiar para considerar se dois retângulos estão intersectando é definido por `THRESHOLD`.
- **Número Máximo de Tentativas:** O número máximo de tentativas para reconhecimento é controlado por `ATTEMPTS`.
- **Deslocamento dos Retângulos:** Os deslocamentos dos retângulos de pergunta e alternativas podem ser ajustados através das variáveis `OFFSETQ` e `OFFSETALT`, respectivamente.
- **Confiança Mínima:** A confiança mínima para detecção de pergunta e alternativa é definida por `CONF1` e `CONF2`, respectivamente.


### Demonstração
https://github.com/Maruquitus/Corretor/assets/58173530/e3cc7c5a-ddb9-4a90-a60c-b07a85a522b7
