import cv2
import numpy as np

##### CASTRO 11/03/2026 - ESSA VERSÃO AQUI TRAVA A ROTAÇÃO DA LINHA VERDE
ver = '\nCASTRO - 11/03/2026\n'
drawing =                       False
first_point =                   None
second_point =                  None
global_first_point =            None
img =                           None
temp_img =                      None
history =                       []  
line =                          0

#__________________________________________________________________________________________________#               #
#__________________________________________________________________________________________________#               ###
#__________________________________________________________________________________________________#               #######
##### CASTRO 11/03/2026 - ALGUNS PARÂMETROS BEM SIMPLES PARA FACILITAR A VISUALIZAÇÃO              #               ###########
espessura_linha_vermelha =      1                                                                  #               ###############
espessura_linha_verde =         2                                                                  #               ###################
comprimento_linha_vermelha =    50                                                                 #               #######################
taamanho_do_texto =             0.5                                                                #               #######################
distancia_entre_textos_X_e_Y =  10                                                                 #               ###################
bloquear_eixo =                 0       # BLOQUEAR EIXO X = 0; # BLOQUEAR EIXO Y = 1               #               ###############
winname =                       'Programa para Medicao de Pixel'                                   #               ###########
#__________________________________________________________________________________________________#               #######
#__________________________________________________________________________________________________#               ###
#__________________________________________________________________________________________________#               #

def draw_perpendicular_line(image, point, direction_point, length, color, thickness):
    dx,dy = direction_point[0] - point[0], direction_point[1] - point[1]
    
    if dx == 0 and dy == 0:
        angle = 0
    else:
        angle = np.arctan2(dy, dx) 
        
    perp_angle = angle + np.pi/2
    
    x1, y1 = int(point[0] + length * np.cos(perp_angle)), int(point[1] + length * np.sin(perp_angle))
    x2, y2 = int(point[0] - length * np.cos(perp_angle)), int(point[1] - length * np.sin(perp_angle))
    
    cv2.line(image, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)

def save_to_history():
    global img, history
    history.append(img.copy())
    
    if len(history) > 20:  
        history.pop(0)

def undo_last():
    global img, temp_img, history, first_point, second_point, drawing
    if history:
        img =           history.pop()  
        temp_img =      img.copy()
        first_point =   None
        second_point =  None
        drawing =       False
        return True
    return False

def mouse_callback(event, x, y, flags, param):
    global drawing, first_point, second_point, global_first_point,img, line,temp_img
    
    if event == cv2.EVENT_RBUTTONDOWN:
        if global_first_point is not None:
            print(global_first_point)

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing =                   True
        first_point =               (x, y)
        if global_first_point is None:
            global_first_point =    first_point
        second_point =              None
        temp_img =                  img.copy()

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            temp_img = img.copy()
            
            if bloquear_eixo == 0:
                second_point = (x, first_point[1]) 
                cv2.putText(temp_img, "EIXO Y BLOQUEADO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 255), 1, cv2.LINE_AA)
            if bloquear_eixo == 1:
                second_point = (first_point[0], y)
                cv2.putText(temp_img, "EIXO X BLOQUEADO", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 255), 1, cv2.LINE_AA)
            
            if first_point and second_point:
                
                ##### CASTRO 11/03/2026 - NEM LEMBRO O QUE EU IA COMENTAR AQUI, MAS TÁ JÓIA
                cv2.line(temp_img, (0, first_point[1]), (img.shape[1], first_point[1]), (100, 100, 100), 1, cv2.LINE_AA)
                
                cv2.line(temp_img, first_point, second_point, (0, 255, 0), espessura_linha_verde)
                draw_perpendicular_line(temp_img, first_point, second_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                draw_perpendicular_line(temp_img, second_point, first_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                
    elif event == cv2.EVENT_LBUTTONUP:
        if drawing:
            
            if bloquear_eixo == 0:
                second_point = (x, first_point[1]) 
            if bloquear_eixo == 1:
                second_point = (first_point[0], y) 

            if first_point and second_point:
                line +=1
                save_to_history()
                
                cv2.line(img, first_point, second_point, (0, 255, 0), espessura_linha_verde)
                
                draw_perpendicular_line(img, first_point, second_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)            
                draw_perpendicular_line(img, second_point, first_point, comprimento_linha_vermelha, (0, 0, 255), espessura_linha_vermelha)
                
                distancia_X = (f'd[x] = {abs(second_point[0]-first_point[0])}')
                distancia_Y = (f'd[y] = {abs(second_point[1]-first_point[1])}')  
                cv2.putText(img, distancia_X, (int(second_point[0])+10, int(second_point[1] - distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (255,90, 0), 1, cv2.LINE_AA)
                cv2.putText(img, distancia_Y, (int(second_point[0])+10, int(second_point[1] + distancia_entre_textos_X_e_Y)),cv2.FONT_HERSHEY_SIMPLEX, taamanho_do_texto, (0, 255, 0), 1, cv2.LINE_AA)
                
                print('LINE ',line,':{', distancia_X,',',distancia_Y,'}')
                
                temp_img = img.copy()
            drawing = False

def main():
    global img, temp_img, first_point, second_point, drawing, history
    
    img = np.zeros((600, 800, 3), dtype=np.uint8)
    temp_img = img.copy()
    history = []  
    
    cv2.namedWindow(winname)
    cv2.setMouseCallback(winname, mouse_callback)
    print(ver)
    print('>'*32,'<'*32)
    print('>'*26,' INSTRUÇÕES', '<'*26)
    print('>'*32,'<'*32,'\n')
    print('1. CLIQUE E ARRASTE O MOUSE PARA DESENHAR LINHAS NA TELA\n')
    print('2. UTILIZE OS ATALHOS DO TECLADO:')
    print('>', ' '*10,'TECLA S:',' '*10,'SALVAR MEDIÇÕES EM ARQUIVO')
    print('>', ' '*10,'TECLA U:',' '*10,'APAGAR ÚLTIMA LINHA')
    print('>', ' '*10,'TECLA C:',' '*10,'APAGAR TODAS AS LINHAS')
    print('')
    
    while True:
        cv2.imshow(winname, temp_img)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('s') or key == ord('S'):
            print('\n>>> SALVANDO MEDIÇÕES...')
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('c') or key == ord('C'):
            answer = input('\n>>> DESEJA APAGAR TODAS AS LINHAS? (PRESSIONE ENTER PARA CONFIRMAR EXCLUSÃO OU TECLE N PARA CANCELAR A OPERAÇÃO)')
            if answer == '':
                    save_to_history()
                    img = np.zeros((600, 800, 3), dtype=np.uint8)
                    temp_img =      img.copy()
                    first_point =   None
                    second_point =  None
                    drawing =       False
                    print('>>> OPERAÇÃO CONCLUÍDA')
            elif answer == 'n' or answer == 'N':
                    print('>>> OPERAÇÃO CANCELADA')
            
        elif key == ord('u') or key == ord('U'):  
            answer = input('\b>>> DESEJA APAGAR A ÚLTIMA LINHA? (PRESSIONE ENTER PARA CONFIRMAR EXCLUSÃO OU TECLE N PARA CANCELAR A OPERAÇÃO)')
            if answer == '':
                if undo_last():
                    print('>>> OPERAÇÃO CONCLUÍDA')
            elif answer == 'n' or answer == 'N':
                    print('>>> OPERAÇÃO CANCELADA')
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
