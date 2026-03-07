# TAMS
Software de Medição de Calibradores Roscados (Thread Angle Measurement Software)

Este software foi desenvolvido para o uso de medição do ângulo de flancos de calibradores roscados externos cilíndricos ou cônicos. Além de exibir o resultado, o software armazena a imagem capturada com os resultados em uma pasta de arquivos determinada pelo usuário.

<img class="center" src="IP 04 Lado Posterior.PNG" alt="Projeção de Perfil de Calibrador Roscado Cilíndrico" style="width: 600px; height: auto">

O algoritmo de detecção espera uma Região de Interesse (ROI) determinada pelo usuário, realiza transformações de cores na imagem, depois aplica um Canny, busca por segmentos de pixels que formam linhas e finalmente calcula o ângulo entre segmentos distintos. Erros de execução são interceptados pelo Exceptions.py.

<img class="center" src="TAMS Menu.PNG" alt="Menu inicial do software" style="width: 600px; height: auto">

<img class="center" src="Select ROI.PNG" alt="Janela de seleção de Região de Interesse (ROI)" style="width: 600px; height: auto">

<img class="center" src="Results.PNG" alt="Resultados de Medição do Calibrador Roscado Cilíndrico" style="width: 600px; height: auto">
