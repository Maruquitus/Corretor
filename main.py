import cv2
import time
from inference import get_roboflow_model
import os
# Limpa o terminal
clear = lambda: os.system('cls')

# Gabarito
GABARITO = 'CDCBCAABDCDCBABBBEBA'

# Se o retângulo de intersecção for maior do que esse valor, os dois retângulos serão considerados como intersectantes
THRESHOLD = 85

# Número máximo de tentativas de detecção
ATTEMPTS = 3

# Deslocamento do retângulo da pergunta
OFFSETQ = (0, 0)

# Deslocamento do retângulo da alternativa
OFFSETALT = (0, 0)

# Confiança mínima para detecção de pergunta
CONF1 = 0.4

# Confiança mínima para detecção de alternativa
CONF2 = 0.6

def intersect(ret1, ret2):
   """
   Verifica se dois retângulos se intersectam e retorna a porcentagem de sobreposição.

   Args:
       ret1: Tupla representando o primeiro retângulo (x, y, w, h).
       ret2: Tupla representando o segundo retângulo (x, y, w, h).

   Returns:
       Porcentagem de sobreposição dos retângulos (0 a 100).
   """
   x1, y1, w1, h1 = ret1[0:4]
   x2, y2, w2, h2 = ret2[0:4]

   # Calcular coordenadas dos cantos dos retângulos
   x_left = max(x1, x2)
   y_top = max(y1, y2)
   x_right = min(x1 + w1, x2 + w2)
   y_bottom = min(y1 + h1, y2 + h2)

   # Calcular a área de interseção
   intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)

   # Calcular a área total de cada retângulo
   area_ret1 = w1 * h1
   area_ret2 = w2 * h2

   # Calcular a porcentagem de sobreposição
   overlap_percentage = (intersection_area / min(area_ret1, area_ret2)) * 100

   return [overlap_percentage > THRESHOLD, overlap_percentage]

# Inicializa o objeto de captura de vídeo
cap = cv2.VideoCapture(2)

# Carrega os modelos
model = get_roboflow_model(model_id="corraut-2pond/5")
modelAlts = get_roboflow_model(model_id='corraut/2')

leituras = []  # Armazena as leituras das alternativas reconhecidas

while True:

   # Lê um frame do webcam
   ret, frame = cap.read()

   # Realiza a detecção de objetos no frame
   results = model.infer(frame, confidence=CONF1, iou_THRESHOLDold=0.6)
   r = time.time()
   results_alt = modelAlts.infer(frame, confidence=CONF2, iou_THRESHOLDold=0.6)

   qRects = {}  # Armazena os retângulos das perguntas
   questões = {}  # Armazena as perguntas e seus respectivos retângulos

   for r in results[0].predictions:  # Verifica as perguntas
       q = r.class_name  # Nome da pergunta
       qRect = (r.x - 50 + OFFSETQ[0], r.y - 12 + OFFSETQ[1], r.width, r.height)  # Retângulo da pergunta
       cv2.rectangle(frame, (int(qRect[0]), int(qRect[1])),
                      (int(qRect[0] + qRect[2]), int(qRect[1] + qRect[3])),
                      color=(0, 255, 0), thickness=1)  # Desenha o retângulo da pergunta
       cv2.putText(frame, q, (int(qRect[0] - 10), int(qRect[1] + 20)),
                   fontFace=1, fontScale=1, thickness=2, color=(255, 255, 255))  # Exibe o nome da pergunta
       qRects[q] = qRect  # Adiciona o retângulo da pergunta no dicionário
       questões[q] = []  # Inicializa a lista de alternativas da pergunta

   lidas = 0  # Número de alternativas lidas
   marcadas = 0  # Número de alternativas marcadas
   for r in results_alt[0].predictions:  # Verifica as alternativas
       if (r.class_name == 'marcada'):  # Se a alternativa estiver marcada
           marcadas += 1  # Incrementa o contador de alternativas marcadas
       altRect = (r.x - 10 + OFFSETALT[0], r.y - 12 + OFFSETALT[1], r.width, r.height, r.class_name)  # Retângulo da alternativa
       for q in qRects.keys():  # Verifica as perguntas
           d = intersect(qRects[q], altRect)  # Verifica se o retângulo da pergunta intersecta com o retângulo da alternativa
           if d[0]:  # Se os retângulos estiverem intersectando
               lidas += 1  # Incrementa o contador de alternativas lidas
               questões[q].append(altRect)  # Adiciona a alternativa à lista de alternativas da pergunta
               cv2.rectangle(frame, (int(altRect[0]), int(altRect[1])),
                              (int(altRect[0] + altRect[2]), int(altRect[1] + altRect[3])),
                              color=(0, 165, 255) if r.class_name == 'marcada' else (140, 140, 140), thickness=1)  # Desenha o retângulo da alternativa
   clear()
   print("###############################")
   print("C o r r A u t  -  2 0 2 4".center(48))
   print("###############################################")
   print(
       f"qRects: {len(qRects.keys())}, altRects: {len(results_alt[0].predictions)}, questões: {len(questões.keys())}, lidas: {lidas}% ({marcadas} marcadas)")
   print("-----------------------------------------------")
   itens = ''  # Armazena as letras das alternativas reconhecidas
   done = True  # Indica se todas as perguntas foram respondidas
   corretos = 0  # Contador de respostas corretas
   for q in range(1, 21):  # Itera sobre as 20 perguntas
       try:
           data = questões[str(q)]  # Obtém as alternativas da pergunta atual
       except:
           data = []  # Se a pergunta não tiver alternativas, inicializa a variável como vazia
       ok = len(data) == 5  # Verifica se a pergunta tem 5 alternativas
       if (not ok):
           done = False  # Se uma pergunta não tiver 5 alternativas, todas as perguntas ainda não foram respondidas
       text = 'lida' if ok else f'{len(data)}/5'
       if ok:
           data.sort(key=lambda x: x[0])  # Ordena as alternativas pela coordenada x do retângulo
           for r in range(5):  # Itera sobre as 5 alternativas
               if (data[r][4] == 'marcada'):  # Se a alternativa estiver marcada
                   item = 'ABCDE'[r]  # Obtém a letra da alternativa
                   itens += item  # Adiciona a letra à string de letras reconhecidas

                   correta = item == GABARITO[q - 1]  # Verifica se a alternativa está correta

                   text += f" ({item}) {'✔️' if correta else '❌'}"  # Exibe a alternativa e o resultado
                   break

       print(f"{'[ok] ' if str(q) in questões.keys() else ''}{q} - {text}", flush=True)
   if done:
       itensFinais = []  # Armazena as letras reconhecidas para cada pergunta
       leituras.append(itens)  # Adiciona as letras reconhecidas à lista de leituras
       if len(leituras) > ATTEMPTS:  # Se o número de leituras for maior que o número máximo de tentativas
           for q in range(20):  # Itera sobre as 20 perguntas
               iList = [0 for _ in range(5)]  # Inicializa a lista de contagens de letras
               for l in leituras:  # Itera sobre as leituras anteriores
                   item = l[q]  # Obtém a letra reconhecida para a pergunta atual
                   iList['ABCDE'.find(item)] += 1  # Incrementa o contador da letra correspondente
               itemProv = 'ABCDE'[iList.index(max(iList))]  # Obtém a letra com o maior número de ocorrências
               itensFinais.append(itemProv)  # Adiciona a letra à lista de letras reconhecidas finalmente
           corretos = 0  # Zera o contador de respostas corretas
           clear()
           print("###############################################")
           print("C o r r A u t  -  2 0 2 4".center(48))
           print("###############################################")
           print(f'Reconhecimento finalizado'.center(48))
           print("-----------------------------------------------")
           for i in range(20):
               item = itensFinais[i]  # Obtém a letra reconhecida finalmente para a pergunta atual
               correta = item == GABARITO[i]  # Verifica se a letra está correta
               if correta: corretos += 1  # Se a letra estiver correta, incrementa o contador de respostas corretas
               print(f"{i + 1} - ({item}) {'✔️' if correta else '❌'}", flush=True)
           leituras = []  # Limpa a lista de leituras
           input(f'* {corretos * 5}% de acertos! Pressione enter para continuar... ')
              
   # Exibir o frame anotado
   cv2.imshow("Frame", frame)

   # Sair do loop ao pressionar q
   if cv2.waitKey(1) & 0xFF == ord('q'):
       break

# Liberar o objeto de captura e fechar as janelas
cap.release()
cv2.destroyAllWindows()