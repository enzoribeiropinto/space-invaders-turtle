
import turtle
import random
import time
import os
import sys

# =========================
# Parâmetros / Constantes
# =========================
LARGURA, ALTURA = 600, 900
BORDA_X = (LARGURA // 2) - 20
BORDA_Y = (ALTURA // 2) - 10

PLAYER_SPEED = 20
PLAYER_BULLET_SPEED = 16
BULLET_COOLDOWN = 0.1  # Cooldown entre tiros (em segundos)
LAST_SHOT_TIME = [0]   # Guarda o momento do último tiro

ENEMY_ROWS = 3
ENEMY_COLS = 10
ENEMY_SIZE = 32
ENEMY_SPACING_X = 18 + ENEMY_SIZE
ENEMY_SPACING_Y = 60
ENEMY_START_Y = BORDA_Y - ENEMY_SIZE    # Topo visível
ENEMY_START_X = - BORDA_X
ENEMY_FALL_SPEED = 0.5
ENEMY_DRIFT_STEP = 2
ENEMY_FIRE_PROB = 0.006
ENEMY_BULLET_SPEED = 8
ENEMY_INVERT_CHANCE = 0.05
ENEMY_DRIFT_CHANCE = 0.5

PLAYER_BULLETS = []
ENEMY_BULLETS = []
COUNTER = 0
COLLISION_RADIUS = 10
HIGHSCORES_FILE = "highscores.txt"
SAVE_FILE = "savegame.txt"
TOP_N = 10

STATE = None  # Usado apenas para callbacks do teclado

# =========================
# Top Resultados (Highscores)
# =========================

def ler_highscores(filename):

    # Lista que guarda todos os scores e nomes de jogadores no formato: (score, nome)
    top_list = []

    # Se o arquivo em questão existe, executar o resto. Se não, retorna 0
    if os.path.exists(filename):
        with open(filename, 'r') as f:

            flines = f.readlines()

            if len(flines) != 0:
                for linha in flines:
                    elementos = linha.strip().split(":")
                    score = elementos[0]
                    jogador = elementos[1]
                    # Adiciona o score e o nome do jogador à top_list
                    top_list.append((int(score), jogador))
        return top_list
    return 0

def atualizar_highscores(filename, score):

    # Guarda a lista com os highscores anteriores, recebida da função ler_highscores()
    top = ler_highscores(filename)
    
    # Pede o nome do jogador e adiciona-o (por meio de "append" ou "insert") junto com seu score à lista de scores
    def addscore(mode = "insert"):
        jogador = input("Gravar score no top? Se sim escreva nome de jogador, senão carregue Return: ")
        
        # Para a execução se o nome recebido do jogador não for composto apenas de letras
        if jogador.isalpha() == False:
            return
        
        # Caso o modo seja "insert", ele insere o score e nome na index adequada para que a lista seja decrescente
        if mode == "insert":
            index = 0
            for i in range(len(top)):
                if int(top[i][0]) >= score:
                    index = i+1
            top.insert(index, (score, jogador))
        
        # Caso o modo seja "append", ele apenas adiciona o score e nome na lista 
        # (Para casos em que não há nenhum score registrado ou não há "highscores.txt")
        elif mode == "append":
            top.append((score, jogador))

        # Escreve os score e nome no arquivo "filename" no formato:
        ###
        # score1:nome1
        # score2:nome2
        # score3:nome3
        ###
        with open(filename, 'w') as f:
            for i in top:
                f.write(f"{i[0]}:{i[1]}\n")
        f.close()

        print("Registo do score bem sucedido")

    # Se a lista foi obtida (ou seja, já existe o arquivo de highscores) 
    # ele executa a função addscore() de modo "insert", para adicionar o score
    if top != 0:
        # Se o tamanho da lista for menor que o máximo ele adiciona o score normalmente
        if len(top)<(TOP_N):
            addscore()

        # Se o tamanho da lista for igual ao máximo adiciona-se o score (caso seja maior que o mínimo da lista) 
        # e deleta-se o último score (para manter o tamanho no limite)
        elif score>top[-1][0]:
            del top[-1]
            addscore()
    # Se a lista está vazia (não havia arquivo de highscores) é executado addscore() no modo "append" 
    # e assim é criado um arquivo de highscores
    else:
        top = []
        addscore("append")
        return

# =========================
# Guardar / Carregar estado (texto)
# =========================

def guardar_estado_txt(filename):
    with open(filename, 'w') as salvar:
        # Recebe o score do dicionário "state"
        pontos = state["score"]
        # Escreve o valor score no arquivo de save (filename)
        salvar.write(f"SCORE {pontos}\n")

        # Recebe a posição do player
        p = state["player"]
        px = p.xcor()
        py = p.ycor()
        # Guarda a posição do player no arquivo de save
        salvar.write(f"PLAYER {px} {py}\n")

        # Itera pelas balas do player em cena
        for pb in state["player_bullets"]:
            # Recebe a posição da bala em questão
            pbx = pb.xcor()
            pby = pb.ycor()
            # Guarda a posição da bala em questão
            salvar.write(f"PLAYER_BULLET {pbx} {pby}\n")
        
        # Itera pelos inimigos em cena
        for e in state["enemies"]:
            # Recebe a posição do inimigo em questão
            ex = e.xcor()
            ey = e.ycor()
            # Guarda a posição do inimigo em questão
            salvar.write(f"ENEMY {ex} {ey}\n")
        
        # Itera pelas balas inimigas em cena
        for eb in state["enemy_bullets"]:
            # Recebe a posição da bala em questão
            ebx = eb.xcor()
            eby = eb.ycor()
            # Guarda a posição da bala em questão
            salvar.write(f"ENEMY_BULLET {ebx} {eby}\n")
        
        # Itera pela lista de vetores de movimento de cada inimigo
        for em in state["enemy_moves"]:
            # Salva o vetor de movimento de cada inimigo
            salvar.write(f"ENEMY_MOVE {em}\n")

    salvar.close()

def carregar_estado_txt(filename):
    # Executa se o nome do ficheiro recebido pelo usuário for válido
    if verificar_nome_ficheiro(filename) != 0:
        filename += ".txt"
        # Executa se o ficheiro existir
        if os.path.exists(filename):    
            # Dicionário dos fatores a ser carregados do arquivo de save
            carregado = {
                "player": None,
                "enemies": [],
                "enemy_moves": [],
                "player_bullets": [],
                "enemy_bullets": [],
                "score": 0,
            }
            # Lê o arquivo de save
            with open(filename, "r") as salvo:
                for linha in salvo:
                    elementos = linha.strip().split()

                    # Define em que fator do dicionário vai ser adicionado o valor
                    tipo = elementos[0]

                    if tipo == "PLAYER":
                        px = float(elementos[1])
                        py = float(elementos[2])
                        carregado["player"] = ("p", px, py)
                    
                    elif tipo == "PLAYER_BULLET":
                        bx = float(elementos[1])
                        by = float(elementos[2])
                        carregado["player_bullets"].append("pb")
                        carregado["player_bullets"].append(bx)
                        carregado["player_bullets"].append(by)
                    
                    elif tipo == "ENEMY":
                        ex = float(elementos[1])
                        ey = float(elementos[2])
                        carregado["enemies"].append("e")
                        carregado["enemies"].append(ex)
                        carregado["enemies"].append(ey)
                    
                    elif tipo == "ENEMY_BULLET":
                        ebx = float(elementos[1])
                        eby = float(elementos[2])
                        carregado["enemy_bullets"].append("eb")
                        carregado["enemy_bullets"].append(ebx)
                        carregado["enemy_bullets"].append(eby)
                    
                    elif tipo == "ENEMY_MOVE":
                        em = float(elementos[1])
                        carregado["enemy_moves"].append("em")
                        carregado["enemy_moves"].append(em)
                    
                    elif tipo == "SCORE":
                        carregado["score"] = int(elementos[1])

            salvo.close()
            return carregado
    # Se o ficheiro não for válido retorna None
    else:
        return None

# =========================
# Criação de entidades (jogador, inimigo e balas)
# =========================

def criar_entidade(state, x, y, tipo="enemy"):
    # Executa se a entidade a ser criada é o player
    if tipo == "player":
        entidade = turtle.Turtle(visible=False, shape="player.gif")
        entidade.up()
        entidade.seth(90)
    # Executa se a entidade a ser criada é o inimigo
    else:
        entidade = turtle.Turtle(visible=False, shape="enemy.gif")
        entidade.up()
        entidade.seth(270)
    # Determina a posição da entidade
    entidade.setpos(x,y)

    entidade.showturtle()
    return entidade

def criar_bala(x, y, tipo):
    # Evitar execução da função após a finalização do jogo
    if state["game"] == "stop":
        return
    # Executar se for uma bala do player
    if tipo=="player":
        # Cria um turtle e define seu ângulo (heading) apontando para o norte
        bala = turtle.Turtle(visible=False, shape="player_bullet.gif")
        bala.up()
        bala.seth(90)
    # Executar se for uma bala do inimigo
    elif tipo=="enemy":
        # Cria um turtle e define seu ângulo (heading) apontando para o sul
        bala = turtle.Turtle(visible=False, shape="enemy_bullet.gif")
        bala.up()
        bala.seth(270)
    bala.setpos(x,y)
    bala.showturtle()
    return bala

def spawn_inimigos_em_grelha(state, carregado=None):
    # Executa caso o jogo não tenha sido carregado
    if carregado==None:
        # Cria as linhas de inimigos
        for r in range(ENEMY_ROWS):
            # Cria as colunas de inimigos
            for c in range(ENEMY_COLS):
                # Define a posição do inimigo no eixo X
                ex = ENEMY_START_X+(ENEMY_SPACING_X*(c+1))
                # Define a posição do inimigo no eixo Y
                ey = (ENEMY_START_Y)-((ENEMY_SPACING_Y)*(r+1))
                # Usa criar_entidade() para gerar o inimigo na posição (ex, ey)
                inimigo = criar_entidade(state, ex, ey, "enemy")
                state["enemies"].append(inimigo)
                state["enemy_moves"].append(ENEMY_DRIFT_STEP)
    # Caso o jogo tenha sido carregado
    else:
        count = 0
        # Recebe vetores de movimento do save
        for n in range(len(carregado["enemy_moves"])):
            if carregado["enemy_moves"][n] == "em":
                movimento = carregado["enemy_moves"][n+1]
                state["enemy_moves"].append(movimento)
        # Recebe posições dos inimigos do save
        for i in range(len(carregado["enemies"])):
            if carregado["enemies"][i] == "e":
                ex = carregado["enemies"][i+1]
                ey = carregado["enemies"][i+2]
                inimigo = criar_entidade(state, ex, ey, "enemy")
                state["enemies"].append(inimigo)
                count += 1

def restaurar_balas(state, carregado=None):
    # Executa caso o jogo tenha sido carregado
    if carregado!=None:
        # Itera cada bala do player a ser carregada
        for i in range(len(carregado["player_bullets"])):
            # Apenas recebe as balas que são do valor "pb" (player_bullets)
            if carregado["player_bullets"][i] == "pb":
                # Recebe as posições X e Y da bala em questão
                pbx = carregado["player_bullets"][i + 1]
                pby = carregado["player_bullets"][i + 2]
                # Cria a bala na respectiva posição e adiciona a bala à lista de balas no state
                state["player_bullets"].append(criar_bala(pbx, pby, "player"))
        # Itera cada bala inimiga a ser carregada
        for k in range(len(carregado["enemy_bullets"])):
            # Apenas recebe as balas que são do valor "eb" (enemy_bullets)
            if carregado["enemy_bullets"][k] == "eb":
                # Recebe as posições X e Y da bala em questão
                ebx = carregado["enemy_bullets"][k + 1]
                eby = carregado["enemy_bullets"][k + 2]
                # Cria a bala na respectiva posição e adiciona a bala à lista de balas no state
                state["enemy_bullets"].append(criar_bala(ebx, eby, "enemy"))
    elif carregado==None:
        return

# =========================
# Handlers de tecla 
# =========================

def mover_esquerda_handler():
    # Evitar execução da função após a finalização do jogo
    if state["game"] == "stop":
        return
    # Recebe o player do dicionário state
    p = STATE["player"]
    # Recebe a posição do player no eixo X e a velocidade de movimento do player
    px = p.xcor()
    ps = PLAYER_SPEED
    # Se o player ao se mover não ultrapassa o player se move
    if px - ps >= -BORDA_X:
        p.setx(px - ps)
    # Se o player ao se mover ultrapassa a borda sua posição é definida na borda
    elif px - ps < -BORDA_X:
        p.setx(-BORDA_X)

def mover_direita_handler():
    # Evitar execução da função após a finalização do jogo
    if state["game"] == "stop":
        return
    # Recebe o player do dicionário state
    p = STATE["player"]
    # Recebe a posição do player no eixo X e a velocidade de movimento do player
    px = p.xcor()
    ps = PLAYER_SPEED
    # Se o player ao se mover não ultrapassa o player se move
    if px + ps <= BORDA_X:
        p.setx(px + ps)
    # Se o player ao se mover ultrapassa a borda sua posição é definida na borda
    elif px - ps > -BORDA_X:
        p.setx(BORDA_X)

def time_since_last_bullet():
    # Define o tempo atual
    thisTime=time.time_ns()/(10**9)
    # Retorna o tempo atual menos o tempo do último tiro (ou seja, o tempo que passou desde o tiro)
    return (thisTime-LAST_SHOT_TIME[0])

def disparar_handler():
    # Evitar execução da função após a finalização do jogo
    if state["game"] == "stop":
        return
    # Executa se o tempo desde o último tiro for maior que o cooldown, se não, a ação disparar não faz nada
    if time_since_last_bullet() >= BULLET_COOLDOWN:
        # Recebe o player do dicionário state
        p = STATE["player"]
        # Recebe a posição do player no eixo X e Y
        px = p.xcor()
        py = p.ycor() + 10 # Adiciona 10 unidades à posição Y para que a bala apareça levemente acima do player
        # Cria a bala do player na posição definida
        bala = criar_bala(px, py, "player")
        # Adiciona a bala à lista de balas
        STATE["player_bullets"].append(bala)
        # Guarda o momento atual como o momento do último tiro (para calcular o cooldown)
        LAST_SHOT_TIME[0] = time.time_ns()/(10**9)

def gravar_handler():
    # Evitar execução da função após a finalização do jogo
    if state["game"] == "stop":
        return
    # A execução de outros comandos para enquanto o processo de gravar não termina
    while True:
        nome = input("Guardar jogo? Se sim, escreva nome do ficheiro, senão carregue Return: ")
        # Se o nome recebido é nulo, a função finaliza
        if nome == "":
            return
        # Se o nome não é nulo, caso seja composto por caracteres ilegais, continua o loop
        elif verificar_nome_ficheiro(nome) == 0:
            print("Escreva nome sem, espaços ou caracteres especiais: ")
            continue
        # Se o nome é valido e não-nulo quebra-se o loop
        elif verificar_nome_ficheiro(nome) == 1:
            nome = nome + ".txt"
            break
    # Guarda o estado com o nome validado
    guardar_estado_txt(nome)

def terminar_handler(tipo="derrota"):
    # Prepara para a tela de finalização
    def prepara():
        # Limpa a tela
        turtle.clearscreen()
        # Define o background como preto novamente
        screen.bgcolor("black")
        # Define a cor da da pen do turtle como branca (para o texto branco da tela final)
        turtle.pencolor("white")
    
    # Escreve o texto da tela final
    def escreve(x, y, title, fontsize):
        # Esconde o turtle
        turtle.hideturtle()
        # penup() para que não a turtle deixe rastro
        turtle.pu()
        # Move o turtle para a posição que o texto vai ser escrito
        turtle.goto(x, y)
        # pendown() para que não a turtle possa escrever o texto
        turtle.pd()
        # Escreve o texto baseado nos argumentos da definição
        turtle.write(title, align ="center", font=("Monospace", fontsize, "bold"))
    state["game"] = "stop"
    score = state["score"]

    # Caso o jogo tenha terminado por conta da eliminação do jogador
    if tipo=="derrota":
        print("GAME OVER - Derrota!")
        prepara()
        escreve(0, 100, "GAME OVER", 60)
        escreve(0, -50, "Score", 30)
        escreve(0, -100, score, 20)
        # Atualiza os highscores
        atualizar_highscores(HIGHSCORES_FILE, score)
        turtle.exitonclick()
    # Caso o jogo tenha terminado por conta da eliminação de todos os inimigos
    elif tipo=="vitoria":
        print("VITÓRIA - Todos os inimigos destruídos!")
        prepara()
        escreve(0, 100, "VITÓRIA", 60)
        escreve(0, -50, "Score", 30)
        escreve(0, -100, score, 20)
        # Atualiza os highscores
        atualizar_highscores(HIGHSCORES_FILE, score)
        turtle.exitonclick()
    # Caso o jogo tenha terminado por clique no botão de escape
    else:
        print("Saiu do jogo (Escape pressionado)")
        prepara()
        escreve(0, 100, "GAME OVER", 60)
        escreve(0, -50, "Score", 30)
        escreve(0, -100, score, 20)
        # Atualiza os highscores
        atualizar_highscores(HIGHSCORES_FILE, score)
        turtle.exitonclick()
    

# =========================
# Atualizações e colisões
# =========================

def atualizar_balas_player(state):
    if state["game"] == "stop":
        return
    listabalas = state["player_bullets"]
    for pb in listabalas:
        pby = pb.ycor()
        if pby != BORDA_Y:
            pb.fd(PLAYER_BULLET_SPEED)
        else:
            pb.hideturtle()
            state["player_bullets"].remove(pb)
        
def atualizar_balas_inimigos(state):
    if state["game"] == "stop":
        return
    listabalas = state["enemy_bullets"]
    for eb in listabalas:
        eby = eb.ycor()
        if eby != -BORDA_Y:
            eb.fd(ENEMY_BULLET_SPEED)
        else:
            eb.hideturtle()
            state["enemy_bullets"].remove(eb)

def atualizar_inimigos(state):
    # Executa se a variável "game" do dicionário "state" contiver a cadeia de caracteres "stop"
    if state["game"] == "stop":
        return
    # Itera os indíces na lista "state["enemies"]"
    for e in range(len(state["enemies"])):
        # Define o inimigo do indíce atual
        enemy = state["enemies"][e]
        # Define a direção do "Drift" do inimigo do indíce atual
        dx = state["enemy_moves"][e]
        # Executa se o valor aleatório for menor ou igual ao valor da variável "ENEMY_DRIFT_CHANCE"
        if random.random() < ENEMY_DRIFT_CHANCE:
            # Adiciona à coordenada x do inimigo do indíce atual o valor do seu "Drift"
            enemy.setx(enemy.xcor() + dx)
        # Altera a coordenada x do inimigo do indíce atual o valor da variável global "ENEMY_FALL_SPEED"
        enemy.sety(enemy.ycor() - ENEMY_FALL_SPEED)
        # Executa se a atual coordenada x do inimigo do indíce atual for maior que a borda direita do ecrã
        if enemy.xcor() > BORDA_X:
            # Iguala a atual coordenada x do inimigo do indíce atual ao valor da borda direita do ecrã
            enemy.setx(BORDA_X)
            # Altera o sentido do "Drift" do inimigo do indíce atual
            dx *= -1
            # Iguala a direção do "Drift" na lista "state["enemy_moves"]" ao "Drift" atual do inimigo do indíce atual
            state["enemy_moves"][e] = dx
        # Executa se a atual coordenada x do inimigo do indíce atual for menor que a borda esquerda do ecrã
        if enemy.xcor() < -BORDA_X:
            # Iguala a atual coordenada x do inimigo do indíce atual ao valor da borda esquerda do ecrã
            enemy.setx(-BORDA_X)
            # Altera o sentido do "Drift" do inimigo do indíce atual
            dx *= -1
            # Iguala a direção do "Drift" na lista "state["enemy_moves"]" ao "Drift" atual do inimigo do indíce atual
            state["enemy_moves"][e] = dx
        # Executa se o valor aleatório for menor ao valor da variável "ENEMY_INVERT_CHANCE"
        if random.random() < ENEMY_INVERT_CHANCE:
            # Altera o sentido do "Drift" do inimigo do indíce atual
            dx *= -1
            # Iguala a direção do "Drift" na lista "state["enemy_moves"]" ao "Drift" atual do inimigo do indíce atual
            state["enemy_moves"][e] = dx

def inimigos_disparam(state):
    # Executa se a variável "game" do dicionário "state" contiver a cadeia de caracteres "stop"
    if state["game"] == "stop":
        return
    # Itera os inimigos
    for e in state["enemies"]:
        # Executa se o valor aleatório for menor ou igual ao valor da variável "ENEMY_FIRE_PROB"
        if random.random() <= ENEMY_FIRE_PROB:
            # Define a atual coordenada x do inimigo
            ex = e.xcor()
            # Define a atual coordenada y do inimigo
            ey = e.ycor()
            # Define a bala criada pela função "criar_bala"
            bala = criar_bala(ex, ey-10, "enemy")
            # Adiciona a bala à lista "state["enemy_bullets"]"
            state["enemy_bullets"].append(bala)
 
def verificar_colisoes_player_bullets(state):
    # Executa se a variável "game" do dicionário "state" contiver a cadeia de caracteres "stop"
    if state["game"] == "stop":
        return
    # Define a lista das balas do player
    listabalas = state["player_bullets"][:]
    # Itera as os indíces da lista das balas do player
    for b in range(len(listabalas)):
        # Define a bala do indíce atual
        bala = listabalas[b]
        # Itera as os indíces da lista "state["enemies"]"
        for n in range(len(state["enemies"])):
            # Define o inimigo do indíce atual
            e = (state["enemies"])[n]
            # Define a atual coordenada x da bala
            bx = bala.xcor()
            # Define a atual coordenada y da bala
            by = bala.ycor()
            # Define a atual coordenada x do inimigo
            ex = e.xcor()
            # Define a atual coordenada y do inimigo
            ey = e.ycor()
            # Define o raio de colisão
            c = COLLISION_RADIUS
            # Executa se as coordenadas da bala estiverem dentro da circunferência 
            # com o seu centro igual às coordenadas do inimigo, e de raio igual ao raio de colisão
            if ex-c < bx < ex+c and ey-c< by < ey+c:
                # Esconde a "turtle" do inimigo
                e.hideturtle()
                # Esconde a "turtle" da bala
                bala.hideturtle()
                # Elimina o inimigo da lista "state["enemies"]"
                del state["enemies"][n]
                # Elimina a bala da lista "state["player_bullets"]"
                del state["player_bullets"][b]
                # Adiciona à variável "Score" do dicionário "state" o valor "10"
                state["score"] += 10
                break
    # Retorna a variável "Score" do dicionário "state"
    return state["score"]

def verificar_colisoes_enemy_bullets(state):
    # Executa se a variável "game" do dicionário "state" contiver a cadeia de caracteres "stop"
    if state["game"] == "stop":
        return
    # Define a lista das balas dos inimigos
    listabalas = state["enemy_bullets"][:]
    # Itera as os indíces da lista das balas dos inimigos
    for b in range(len(listabalas)):
        # Define o player
        p = state["player"]
        # Define a bala do indíce atual
        bala = listabalas[b]
        # Define a atual coordenada x da bala
        ebx = bala.xcor()
        # Define a atual coordenada y da bala
        eby = bala.ycor()
        # Define a atual coordenada x do player
        px = p.xcor()
        # Define a atual coordenada y do player
        py = p.ycor()
        # Define o raio de colisão
        c = COLLISION_RADIUS
        # Executa se as coordenadas da bala estiverem dentro da circunferência 
        # com o seu centro igual às coordenadas do player, e de raio igual ao raio de colisão
        if px-c < ebx < px+c and py-c < eby < py+c:
            # Esconde a "turtle" da bala
            bala.hideturtle()
            # Esconde a "turtle" do player
            p.hideturtle()
            # Elimina a bala da lista "state["enemy_bullets"]"
            del state["enemy_bullets"][b]
            # Retorna a cadeia de carateres "over"
            return "over"

def inimigo_chegou_ao_fundo(state):
    # Itera os inimigos
    for enemy in state["enemies"]:
        # Define a atual coordenada y do inimigo
        ey = enemy.ycor()
        # Executa se a coordenada y do inimigo for menor que borda negativa y do ecrã
        if ey < -BORDA_Y:
            # Retorna a cadeia de carateres "over"
            return "over"

def verificar_colisao_player_com_inimigos(state):
    # Executa se a variável "game" do dicionário "state" contiver a cadeia de caracteres "stop"
    if state["game"] == "stop":
        return
    # Define o player
    player = state["player"]
    # Define a atual coordenada x do player
    px = player.xcor()
    # Define a atual coordenada y do player 
    py = player.ycor()
    # Define o raio de colisão
    c = COLLISION_RADIUS
    # Itera os inimigos
    for enemy in state["enemies"]:
        # Define a atual coordenada x do inimigo
        ex = enemy.xcor()
        # Define a atual coordenada y do inimigo
        ey = enemy.ycor()
        # Executa se as coordenadas do inimigo estiverem dentro da circunferência 
        # com o seu centro igual às coordenadas do player, e de raio igual ao raio de colisão
        if (px-c) < ex < (px+c) and py+c > ey:
            # Esconde a "turtle" do player
            player.hideturtle()
            # Esconde a "turtle" do inimigo
            enemy.hideturtle()
            # Retorna a cadeia de carateres "over"
            return "over"

def verificar_nome_ficheiro(filename):
    # Executa se argumento for exclusivamente composto por letras 
    if filename.isalpha() == True:
        # Retorna o valor "1"
        return 1
    # Retorna o valor "0"
    return 0

def lista_todas_balas(state):
    # Executa se a variável global "COUNTER" for menor que "1"
    if COUNTER < 1:
        # Adiciona "1" à variável global "COUNTER"
        COUNTER += 1
        return
    # Executa se a variável global "COUNTER" for igual a "1"
    elif COUNTER == 1:
        # Itera as balas do player
        for pb in state["player_bullets"]:
            # Adiciona a bala à lista global "PLAYER_BULLETS"
            PLAYER_BULLETS.append(pb)
        # Itera as balas dos inimigos
        for eb in state["enemy_bullets"]:
            # Adiciona a bala à lista global "ENEMY_BULLETS"
            ENEMY_BULLETS.append(eb)
        # Iguala a variável global "COUNTER" a "0"
        COUNTER = 0

def verificar_turtle_bug():
    # Itera as balas do player
    for pb in state["player_bullets"]:
        # Define a atual coordenada x da bala 
        pbx = pb.xcor()
        # Define a atual coordenada y da bala 
        pby = pb.ycor()
        # Define o indíce da bala 
        index = state["player_bullets"].index(pb)
        # Define a passada coordenada x da bala 
        pastx = PLAYER_BULLETS[index].xcor()
        # Define a passada coordenada y da bala 
        pasty = PLAYER_BULLETS[index].ycor()
        # Executa se as coordenadas atuais e passadas forem iguais a bala
        if pbx == pastx and pby == pasty:
            # Esconde a bala
            pb.hideturtle()
            # Remove a bala da lista "state["player_bullets"]"
            state["player_bullets"].remove(index)
    # Itera as balas dos inimigos
    for eb in state["enemy_bullets"]:
        # Define a atual coordenada x da bala 
        ebx = eb.xcor()
        # Define a atual coordenada y da bala 
        eby = eb.ycor()
        # Define o indíce da bala 
        index = state["enemy_bullets"].index(eb)
        # Define a passada coordenada x da bala 
        pastx = ENEMY_BULLETS[index].xcor()
        # Define a passada coordenada y da bala 
        pasty = ENEMY_BULLETS[index].ycor()
        # Executa se as coordenadas atuais e passadas forem iguais a bala
        if ebx == pastx and eby == pasty:
            # Esconde a bala
            eb.hideturtle()
            # Remove a bala da lista da "state["enemy_bullets"]"
            state["enemy_bullets"].remove(index)
            


# =========================
# Execução principal
# =========================

if __name__ == "__main__":
    # Pergunta inicial: carregar?
    filename = input("Carregar jogo? Se sim, escreva nome do ficheiro, senão carregue Return: ").strip()
    carregado = carregar_estado_txt(filename)

    # Ecrã
    screen = turtle.Screen()
    screen.title("Space Invaders IPRP")
    screen.bgcolor("black")
    screen.setup(width = LARGURA, height = ALTURA, startx = None, starty = None)
    screen.tracer(0)

    # Imagens obrigatórias
    for img in ["player.gif", "enemy.gif", "player_bullet.gif", "enemy_bullet.gif"]:
        if not os.path.exists(img):
            print("ERRO: imagem '" + img + "' não encontrada.")
            sys.exit(1)
        screen.addshape(img)

    # Estado base
    state = {
        "screen": screen,
        "player": None,
        "enemies": [],
        "enemy_moves": [],          
        "player_bullets": [],
        "enemy_bullets": [],
        "score": 0,
        "frame": 0,
        "files": {"highscores": HIGHSCORES_FILE, "save": SAVE_FILE},
        "game": "playing",
    }

    # Construção inicial
    if carregado != None:
        if carregado.get("player"):
            px = carregado["player"][1]
            py = carregado["player"][2]
            state["player"] = criar_entidade(state, px, py, "player")
        else:
            state["player"] = criar_entidade(state, 0, -350, "player")
        if carregado.get("score"):
            state["score"] = carregado.get("score")
        else:
            state["score"] = 0
        spawn_inimigos_em_grelha(state, carregado)
        restaurar_balas(state, carregado)
    else:
        print("New game!")
        jogador = criar_entidade(state, 0, -350, "player")
        state["player"] = jogador
        inimigo = spawn_inimigos_em_grelha(state)

    # Variavel global para os keyboard key handlers
    STATE = state

    # Teclas
    screen.listen()
    screen.onkeypress(mover_esquerda_handler, "Left")
    screen.onkeypress(mover_direita_handler, "Right")
    if time_since_last_bullet() >= BULLET_COOLDOWN:
        screen.onkeypress(disparar_handler, "space")
        LAST_SHOT_TIME[0] = time.time_ns()/(10**9)
    screen.onkeypress(gravar_handler, "g")
    screen.onkeypress(terminar_handler, "Escape")

    # Loop principal
    while True:
        atualizar_balas_player(STATE)
        atualizar_inimigos(STATE)
        inimigos_disparam(STATE)
        atualizar_balas_inimigos(STATE)
        verificar_colisoes_player_bullets(STATE)
        
        if verificar_colisao_player_com_inimigos(STATE)=="over":
            state["game"] = "stop"
            terminar_handler("derrota")
        
        elif verificar_colisoes_enemy_bullets(STATE)=="over":
            state["game"] = "stop"
            terminar_handler("derrota")

        elif inimigo_chegou_ao_fundo(STATE)=="over":
            state["game"] = "stop"
            terminar_handler("derrota")

        elif len(STATE["enemies"]) == 0:
            state["game"] = "stop"
            terminar_handler("vitoria")

        STATE["frame"] += 1
        screen.update()
        time.sleep(0.016)