# TAMS
Software de Medição de Calibradores Roscados (Thread Angle Measurement Software)

Este software foi desenvolvido para o uso de medição do ângulo de flancos de calibradores roscados externos cilíndricos ou cônicos. Além de exibir o resultado, o software armazena a imagem capturada com os resultados em uma pasta de arquivos determinada pelo usuário.

<img src="IP 04 Lado Posterior.png" alt="Projeção de Perfil de Calibrador Roscado Cilíndrico">

O algoritmo de detecção espera uma Região de Interesse (ROI) determinada pelo usuário, realiza transformações de cores na imagem, depois aplica um Canny, busca por segmentos de pixels que formam linhas e finalmente calcula o ângulo entre segmentos distintos. Erros de execução são interceptados pelo Exceptions.py.
