from PIL import Image
import os

def cor_bate(pixel, cor_alvo, tolerancia=15):
    r, g, b = pixel[:3]
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_padrao(imagem, tolerancia=15):
    """
    Percorre a faixa horizontal x=300 a 850 de cima para baixo procurando o padrão:
    - 2px (±1) de (35, 31, 32)
    - 2px (±1) de (255, 255, 255)
    - 4px (±1) de (35, 31, 32)
    - 2px (±1) de (255, 255, 255)
    - 2px (±1) de (35, 31, 32)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Define os limites da faixa horizontal de varredura
    x_inicio = min(300, largura - 1)
    x_fim = min(850, largura)
    
    # Sequência: (cor_alvo, altura_minima, altura_maxima) -> margem de ±1 pixel
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    sequencia = [
        (cor_escura, 1, 3),  # 2px ± 1
        (cor_branca, 1, 3),  # 2px ± 1
        (cor_escura, 3, 5),  # 4px ± 1
        (cor_branca, 1, 3),  # 2px ± 1
        (cor_escura, 1, 3),  # 2px ± 1
    ]
    
    posicoes_corte = []
    y = 0
    
    # Precisa de pelo menos 7 pixels (soma das alturas mínimas) até o fim da imagem
    while y < altura - 7:
        y_atual = y
        padrao_encontrado = True
        
        for cor_alvo, h_min, h_max in sequencia:
            contagem = 0
            while y_atual < altura and contagem < h_max:
                # Verifica se toda a linha horizontal (x de 300 a 850) tem a cor alvo
                linha_valida = True
                for x in range(x_inicio, x_fim):
                    if not cor_bate(pixels[x, y_atual], cor_alvo, tolerancia):
                        linha_valida = False
                        break
                
                if linha_valida:
                    contagem += 1
                    y_atual += 1
                else:
                    break
            
            # Se a altura encontrada ficou fora da margem (±1 px), o padrão falhou
            if contagem < h_min:
                padrao_encontrado = False
                break
        
        if padrao_encontrado:
            posicao_corte = max(0, y - 14)
            posicoes_corte.append(posicao_corte)
            print(f"Padrão encontrado começando em y={y}, cortando em y={posicao_corte}")
            # Pula o padrão inteiro para evitar detecções duplicadas
            y = y_atual
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando 14px ANTES do padrão encontrado
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_padrao(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão encontrado na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} padrões para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa exatamente onde a anterior cortou,
        # preservando os 14px acima do padrão no início da nova imagem
        posicao_anterior = posicao_corte
    
    # Corta a seção final
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes"          # Substitua pelo nome da pasta de saída desejada

    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    print("Divisão concluída!")
