import turtle
import time
import random

# Configurações iniciais
delay = 0.1
score = 0
high_score = 0

# Configuração da tela
wn = turtle.Screen()
wn.title("Jogo da Cobrinha (Snake)")
wn.bgcolor("black")
wn.setup(width=600, height=600)
wn.tracer(0) # Desliga as atualizações automáticas de tela para maior controle

# Cabeça da cobra
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("green")
head.penup()
head.goto(0,0)
head.direction = "stop"

# Comida da cobra
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0,100)

# Corpo da cobra (Lista de segmentos)
segments = []

# Placar
pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0  High Score: 0", align="center", font=("Courier", 24, "normal"))

# Funções de movimentação
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

def move():
    # Movimentação em grade (passos de 20 pixels)
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

# Mapeamento do teclado
wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")

# Loop principal do jogo
try:
    while True:
        wn.update()

        # Verifica colisão com a borda
        if head.xcor()>290 or head.xcor()<-290 or head.ycor()>290 or head.ycor()<-290:
            time.sleep(1)
            head.goto(0,0)
            head.direction = "stop"

            # Esconde os segmentos fora da tela
            for segment in segments:
                segment.goto(1000, 1000)
            
            # Limpa a lista de segmentos
            segments.clear()

            # Reseta o score e a dificuldade
            score = 0
            delay = 0.1

            pen.clear()
            pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal")) 

        # Verifica colisão com a comida
        if head.distance(food) < 20:
            # Geração aleatória de comida na grade de 20px
            x = random.randint(-14, 14) * 20
            y = random.randint(-14, 14) * 20
            food.goto(x, y)

            # Adiciona um novo segmento ao corpo da cobra
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("lightgreen")
            new_segment.penup()
            segments.append(new_segment)

            # Aumento de dificuldade (diminui o tempo de espera/delay)
            delay -= 0.003
            if delay < 0.02: # Limite máximo de velocidade
                delay = 0.02

            # Aumenta o score
            score += 10

            if score > high_score:
                high_score = score
            
            pen.clear()
            pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal")) 

        # Move os segmentos do corpo em ordem inversa (do último para o primeiro)
        for index in range(len(segments)-1, 0, -1):
            x = segments[index-1].xcor()
            y = segments[index-1].ycor()
            segments[index].goto(x, y)

        # Move o segmento 0 para onde a cabeça está
        if len(segments) > 0:
            x = head.xcor()
            y = head.ycor()
            segments[0].goto(x,y)

        move()    

        # Verifica colisão da cabeça com os segmentos do corpo
        for segment in segments:
            if segment.distance(head) < 20:
                time.sleep(1)
                head.goto(0,0)
                head.direction = "stop"
            
                for segment in segments:
                    segment.goto(1000, 1000)
            
                segments.clear()
                score = 0
                delay = 0.1
            
                pen.clear()
                pen.write("Score: {}  High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))

        time.sleep(delay)

except turtle.Terminator:
    pass
