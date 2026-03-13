##### ÂNGULO

import cv2
import numpy as np
from numpy                      import pi,sin,cos,atan2,sqrt,zeros,uint8,arctan2,arccos
from time                       import strftime
from os                         import getcwd, startfile

from reportlab.pdfgen           import canvas
from reportlab.lib.pagesizes    import A4

##### CASTRO 11/03/2026 - ESSA VERSÃO AQUI TRAVA A ROTAÇÃO DA LINHA VERDE
ver = '\nCASTRO - 12/03/2026\n'
drawing =                       False
first_point =                   None
second_point =                  None
global_first_point =            None
img =                           None
temp_img =                      None
history =                       []  
line =                          0
line_measurements =             []  
camera_active =                 True

selecting_lines =               False
selected_lines =                []  
line_selection_mode =           False
hover_point =                   None
angle_measurements =            []  

#__________________________________________________________________________________________________#               #
#__________________________________________________________________________________________________#               ###
#__________________________________________________________________________________________________#               #######
##### CASTRO 11/03/2026 - ALGUNS PARÂMETROS BEM SIMPLES PARA FACILITAR A VISUALIZAÇÃO              #               ###########
espessura_linha_vermelha =      1                                                                  #               ###############
espessura_linha_verde =         1                                                                  #               ###################
comprimento_linha_vermelha =    50                                                                 #               #######################
taamanho_do_texto =             0.5                                                                #               #######################
distancia_entre_textos_X_e_Y =  10                                                                 #               ###################
bloquear_eixo =                 1       # BLOQUEAR EIXO X = 1; # BLOQUEAR EIXO Y = 0               #               ###############
winname =                       'Programa para Medicao de Pixel - Angulo'                          #               ############
winname2 =                      'Cursor Zoom'                                                      #               ##########
#__________________________________________________________________________________________________#               #######
#__________________________________________________________________________________________________#               ###
#__________________________________________________________________________________________________#               #

COR_LINHA_SELECIONADA =         (255,   255,    0)  
COR_LINHA_NORMAL =              (0,     255,    0)    
COR_ANGULO =                    (0,     255,      255)  
COR_TEXTO_ANGULO =              (255,   255,    255)
RAIO_PONTO_SELECAO =            8
COR_PONTO_SELECAO =             (0,     255,    255)  

##### CASTRO 12/03/2026 - ESSE É PARA SALVAR O NOME DO ARQUIVO, ENTÃO REMOVI CARACTERES PROIBIDOS PELO WIN_EXPLORER
def log():
    log = strftime("%d_%m_%Y %H-%M-%S")
    return str(log)

##### CASTRO 12/03/2026 - O LOG2 É PARA IMPRIMIR NO PDF
def log2():
    log = strftime("%d/%m/%Y - %H:%M:%S")
    return str(log)

def draw_perpendicular_line(image, point, direction_point, length, color, thickness):
    dx,dy = direction_point[0] - point[0], direction_point[1] - point[1]
    
    if dx == 0 and dy == 0:
        angle = 0
    else:
        angle = arctan2(dy, dx) 
        
    perp_angle = angle + pi/2
    
    x1, y1 = int(point[0] + length * cos(perp_angle)), int(point[1] + length * sin(perp_angle))
    x2, y2 = int(point[0] - length * cos(perp_angle)), int(point[1] - length * sin(perp_angle))
    
    cv2.line(image, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)

def calculate_angle_between_lines(line1, line2):
    
    dx1, dy1 = line1['second_point'][0] - line1['first_point'][0], line1['second_point'][1] - line1['first_point'][1]
    dx2, dy2 = line2['second_point'][0] - line2['first_point'][0], line2['second_point'][1] - line2['first_point'][1]
    
    dot_product = dx1*dx2 + dy1*dy2
    mag1, mag2 = sqrt(dx1**2 + dy1**2), sqrt(dx2**2 + dy2**2)
    
    if mag1 == 0 or mag2 == 0:
        return 0
    
    cos_angle = dot_product / (mag1 * mag2)
    
    cos_angle = max(-1, min(1, cos_angle))
    
    angle_rad = arccos(cos_angle)
    angle_deg = angle_rad * 180 / pi
    
    return angle_deg, (180 - angle_deg)

def find_nearest_line(x, y, threshold=20):
    
    min_dist = float('inf')
    nearest_line_idx = -1
    
    for i, line in enumerate(line_measurements):
        p1 = np.array(line['first_point'])
        p2 = np.array(line['second_point'])
        p = np.array([x, y])
        
        line_vec = p2 - p1
        point_vec = p - p1
        
        line_len_sq = np.dot(line_vec, line_vec)
        if line_len_sq == 0:
            continue
            
        t = np.dot(point_vec, line_vec) / line_len_sq
        t = max(0, min(1, t))
        proj_point = p1 + t * line_vec
        
        dist = np.linalg.norm(p - proj_point)
        
        if dist < min_dist and dist < threshold:
            min_dist = dist
            nearest_line_idx = i
    
    return nearest_line_idx

def save_to_history():
    global img, history
    history.append(img.copy())
    
    if len(history) > 100:  
        history.pop(0)

def undo_last():
    global img, temp_img, history, first_point, second_point, drawing, line_measurements, line
    if history:
        img =           history.pop()  
        temp_img =      img.copy()
        first_point =   None
        second_point =  None
        drawing =       False
        
        if line_measurements:
            line_measurements.pop()
            line = len(line_measurements)
        return True
    return False

def mouse_callback(event, x, y, flags, param):
    global drawing, first_point, second_point, global_first_point, img, line, temp_img
    global selecting_lines, selected_lines, line_selection_mode, hover_point

    if event == cv2.EVENT_FLAG_CTRLKEY:
        print('control')
    
    if event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY):
        line_idx = find_nearest_line(x, y)
        if line_idx != -1:
            if line_idx in selected_lines:
                selected_lines.remove(line_idx)
                print(f"> LINHA {line_idx+1} REMOVIDA DA SELEÇÃO")
            else:
                selected_lines.append(line_idx)
                print(f"> LINHA {line_idx+1} SELECIONADA")

            if len(selected_lines) == 2:
                angle = calculate_angle_between_lines(line_measurements[selected_lines[0]],line_measurements[selected_lines[1]])
                angle_measurements.append({'lines': (selected_lines[0], selected_lines[1]),'angle': min(angle)})
                print(f'ANGLE | LINE ({selected_lines[0]+1}, {selected_lines[1]+1}) | ',round(angle[0],7),'[deg] | ',round(angle[1],7),'[deg]')
                
                selected_lines = []
        return
    
    if event == cv2.EVENT_MOUSEMOVE:
        if not drawing:  
            line_idx = find_nearest_line(x, y, threshold=15)
            if line_idx != -1:
                hover_point = (x, y, line_idx)
            else:
                hover_point = None
    
    if not (flags & cv2.EVENT_FLAG_CTRLKEY):
        if event == cv2.EVENT_RBUTTONDOWN:
            if global_first_point is not None:
                
                first_point = global_first_point
                
                if bloquear_eixo == 0:
                    first_point = (first_point[0], y) 
                if bloquear_eixo == 1:
                    first_point = (x, first_point[1]) 

                drawing = True
                temp_img = img.copy()
        
        if event == cv2.EVENT_RBUTTONUP:
            if drawing:
                
                if bloquear_eixo == 0:
                    second_point = (x, first_point[1]) 
                if bloquear_eixo == 1:
                    second_point = (first_point[0], y) 

                if first_point and second_point:
                    line +=1
                    save_to_history()
                    
                    cv2.line(img, first_point, second_point, COR_LINHA_NORMAL, espessura_linha_verde)
                    
                    draw_perpendicular_line(img, first_point, second_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)            
                    draw_perpendicular_line(img, second_point, first_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                    
                    dx = abs(second_point[0]-first_point[0])
                    dy = abs(second_point[1]-first_point[1])
                    length = sqrt(dx**2 + dy**2)
                    
                    measurement = {'dx': dx,'dy': dy,'length': length,'first_point': first_point,'second_point': second_point}
                    line_measurements.append(measurement)
                    
                    distancia_X = (f'd[x] = {dx}')
                    distancia_Y = (f'd[y] = {dy}')  
                    #cv2.putText(img, distancia_X, (int(second_point[0])+10, int(second_point[1] - distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (255,90, 0), 1, cv2.LINE_AA)
                    #cv2.putText(img, distancia_Y, (int(second_point[0])+10, int(second_point[1] + distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 0), 1, cv2.LINE_AA)
                    
                    print('LINE ',line,':{', distancia_X,',',distancia_Y,'}', f'{length:.0f} [p]')
                    
                    temp_img = img.copy()
                drawing = False

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            first_point = (x, y)
            if global_first_point is None:
                global_first_point = first_point
            second_point = None
            temp_img = img.copy()

        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                temp_img = img.copy()
                
                second_point = (x, y)
                        
                if first_point and second_point:
                    
                    cv2.line(temp_img, (first_point[0]-int(temp_img.shape[0]), first_point[1]), (img.shape[1], first_point[1]), (100, 100, 100), 1, cv2.LINE_AA)
                    cv2.line(temp_img, (first_point[0], int(temp_img.shape[0]+10)), (first_point[0], -int(temp_img.shape[0]-10)), (100, 100, 100), 1, cv2.LINE_AA)
                    
                    cv2.line(temp_img, first_point, second_point, COR_LINHA_NORMAL, espessura_linha_verde)
                    draw_perpendicular_line(temp_img, first_point, second_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                    draw_perpendicular_line(temp_img, second_point, first_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                    
        elif event == cv2.EVENT_LBUTTONUP:
            if drawing:
                
                second_point = (x,y)

                if first_point and second_point:
                    line +=1
                    save_to_history()
                    
                    cv2.line(img, first_point, second_point, COR_LINHA_NORMAL, espessura_linha_verde)
                    
                    draw_perpendicular_line(img, first_point, second_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)            
                    draw_perpendicular_line(img, second_point, first_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                    
                    dx,dy = abs(second_point[0]-first_point[0]), abs(second_point[1]-first_point[1])
                    length = sqrt(dx**2 + dy**2)
                    
                    measurement = {'dx': dx,'dy': dy,'length': length,'first_point': first_point,'second_point': second_point}
                    line_measurements.append(measurement)
                    
                    distancia_X, distancia_Y = (f'd[x] = {dx}'), (f'd[y] = {dy}')
                    #cv2.putText(img, distancia_X, (int(second_point[0])+10, int(second_point[1] - distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (255,90, 0), 1, cv2.LINE_AA)
                    #cv2.putText(img, distancia_Y, (int(second_point[0])+10, int(second_point[1] + distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 0), 1, cv2.LINE_AA)
                    
                    print('LINE ',line,':{', distancia_X,',',distancia_Y,'}', f'{length:.0f} [p]')
                    
                    temp_img = img.copy()
                drawing = False

def save_to_file(content):
    filename=f'Medições {log()}.pdf'
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 14)
    c.drawString(int((width/3)-15), 800, f'Medições em {log2()}')
    
    c.setFont("Helvetica", 12)
    h = 760
    for i in content:
        c.drawString(50, h, i)
        h-=20

    c.showPage()
    c.save()
    path = (f'{getcwd()}\{filename}')
    print(f"\n>>> MEDIÇÕES SALVAS EM: \n {path}")
    startfile(path)
    print('\n\n')

def save(content):
    save_to_file(content)

def main():
    global img, temp_img, first_point, second_point, drawing, history, line_measurements, line, camera_active
    global selected_lines, hover_point, angle_measurements
    
    cap = cv2.VideoCapture(0)  
    if not cap.isOpened():
        print("> ERRO: NÃO FOI POSSÍVEL ABRIR A CÂMERA")
        return
    
    ret, frame = cap.read()
    if ret:
        img = frame.copy()
    else:
        print("> ERRO: NÃO FOI POSSÍVEL CAPTURAR O FRAME")
        cap.release()
        return
    
    temp_img =              img.copy()
    history =               []  
    line_measurements =     []  
    line =                  0
    selected_lines =        []
    hover_point =           None
    angle_measurements =    []
    
    cv2.namedWindow(winname)
    cv2.setMouseCallback(winname, mouse_callback)
    print(ver)
    print('>'*32,'<'*32)
    print('>'*26,' INSTRUÇÕES', '<'*26)
    print('>'*32,'<'*32,'\n')
    print('1. CLIQUE E ARRASTE O MOUSE PARA DESENHAR LINHAS NA TELA\n')
    print('2. INSTRUÇÕES DE USO:')
    print('   - (Ctrl) + (Clique esquerdo): SELECIONA LINHAS PARA MEDIR ÂNGULO \n')
    print('3. UTILIZE OS ATALHOS DO TECLADO:')
    print('>', ' '*10,'TECLA S:',' '*10,'SALVAR MEDIÇÕES EM ARQUIVO')
    print('>', ' '*10,'TECLA U:',' '*10,'APAGAR ÚLTIMA LINHA')
    print('>', ' '*10,'TECLA C:',' '*10,'APAGAR TODAS AS LINHAS')
    print('>', ' '*10,'TECLA Q:',' '*10,'SAIR DO APP')
    print('>', ' '*10,'TECLA P:',' '*10,'PAUSAR/CONTINUAR CAMERA')
    print('>', ' '*10,'TECLA A:',' '*10,'LISTAR ÂNGULOS MEDIDOS')
    print('')
    
    while True:
        
        if camera_active:
            ret, frame = cap.read()
            if ret:
                if len(line_measurements) > 0 or drawing:
                    img = frame.copy()
                    for i, measurement in enumerate(line_measurements):
                        
                        if i in selected_lines:
                            line_color = COR_LINHA_SELECIONADA
                        else:
                            line_color = COR_LINHA_NORMAL
                        
                        cv2.line(img, measurement['first_point'], measurement['second_point'], line_color, espessura_linha_verde)
                        draw_perpendicular_line(img, measurement['first_point'], measurement['second_point'], comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                        draw_perpendicular_line(img, measurement['second_point'], measurement['first_point'], comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                        #cv2.putText(img, f'd[x] = {measurement["dx"]}', (int(measurement['second_point'][0])+10, int(measurement['second_point'][1] - distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (255,90, 0), 1, cv2.LINE_AA)
                        #cv2.putText(img, f'd[y] = {measurement["dy"]}', (int(measurement['second_point'][0])+10, int(measurement['second_point'][1] + distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 0), 1, cv2.LINE_AA)
                    
                    temp_img = img.copy()

                else:
                    img = frame.copy()
                    temp_img = img.copy()
        
        display_img = temp_img.copy()
        
        if hover_point is not None and not drawing:
            x, y, line_idx = hover_point
            ##### CÍRCULO AMARELO
            cv2.circle(display_img, (x, y), RAIO_PONTO_SELECAO, COR_PONTO_SELECAO, 1)
            cv2.putText(display_img, f"LINE {line_idx+1}", (x+15, y-15),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COR_PONTO_SELECAO, 1, cv2.LINE_AA)
        
        if selected_lines:
            info_text = f"LINE: {[i+1 for i in selected_lines]}"
            cv2.putText(display_img, info_text, (10, 60),cv2.FONT_HERSHEY_SIMPLEX, 0.6, COR_LINHA_SELECIONADA, 1, cv2.LINE_AA)
        
        if angle_measurements:
            last_angle = angle_measurements[-1]
            angle_text = f"RESULT: {last_angle['angle']:.0f} [deg]"
            cv2.putText(display_img, angle_text, (10, 90),cv2.FONT_HERSHEY_SIMPLEX, 0.6, COR_ANGULO, 1, cv2.LINE_AA)
        
        status_color = (0, 255, 0) if camera_active else (0, 0, 255)
        status_text = "AO VIVO" if camera_active else "PAUSE"
        cv2.putText(display_img, status_text, (10, display_img.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1, cv2.LINE_AA)
        
        cv2.imshow(winname, display_img)
            
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            print('\n')
            print('>'*32,'<'*33)
            print('>'*23,' SALVANDO MEDIÇÕES', '<'*23)
            print('>'*32,'<'*33,'\n')
            list_results = []
            avg_list = []
            
            if angle_measurements:
                
                for i, angle_data in enumerate(angle_measurements, 1):
                    list_results.append(f'>>> ANGLE {i} | LINE ({angle_data["lines"][0]+1}, {angle_data["lines"][1]+1}) | {angle_data["angle"]:.7f} [deg]')

            if avg_list:  
                avg = sum(avg_list)/len(avg_list)
                print(f'\n > MÉDIA: {avg}')
                std = []
                for i in avg_list:
                    std.append((i-avg)**2)
                desv_pad = sqrt(sum(std)/(len(avg_list)-1))
                print(f' > DESV.PAD: {desv_pad}')
            save(list_results)
        
        if key == ord('a') or key == ord('A'):
            if angle_measurements:
                print('\n>>> ÂNGULOS MEDIDOS:')
                for i, angle_data in enumerate(angle_measurements, 1):
                    print(f'   {i}: {angle_data["angle"]:.2f}° (entre linhas {angle_data["lines"][0]+1} e {angle_data["lines"][1]+1})')
            else:
                print('\n>>> NENHUM ÂNGULO MEDIDO AINDA')
        
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('p') or key == ord('P'):
            camera_active = not camera_active
            status = "EM USO" if camera_active else "PAUSADA"
            print(f'\n>>> CAMERA {status}\n')
            
        elif key == ord('c') or key == ord('C'):
            answer = input('\n>>> DESEJA APAGAR TODAS AS LINHAS? (PRESSIONE ENTER PARA CONFIRMAR EXCLUSÃO OU TECLE N PARA CANCELAR A OPERAÇÃO)')
            if answer == '':
                    if camera_active:
                        ret, frame = cap.read()
                        if ret:
                            img = frame.copy()
                    else:
                        img = zeros((display_img.shape[0], display_img.shape[1], 3), dtype=uint8)
                    
                    temp_img =                  img.copy()
                    first_point =               None
                    second_point =              None
                    drawing =                   False
                    line_measurements =         []  
                    line =                      0
                    history =                   []
                    selected_lines =            [] 
                    angle_measurements =        []  
                    print('>>> OPERAÇÃO CONCLUÍDA')

            elif answer == 'n' or answer == 'N':
                    print('>>> OPERAÇÃO CANCELADA')

        elif key == ord('u') or key == ord('U'):  
                if undo_last():
                    
                    selected_lines = []
                    print('>>> OPERAÇÃO CONCLUÍDA')
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()