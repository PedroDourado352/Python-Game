# Parkour Master

Um jogo 2D de parkour feito em **Python** com **Pygame**. Pule entre plataformas, desvie de espinhos, use o pulo duplo e chegue até a bandeira no final da fase no menor tempo possível.

## Pré-requisitos

- Python 3.10+ instalado
- Pygame 2.x

## Instalação

Clone o repositório e instale a dependência:

```bash
git clone https://github.com/PedroDourado352/Game-python.git
cd Game-python
pip install pygame
```

Se o comando `python` não estiver disponível no Windows (atalho da Microsoft Store), use:

```bash
py -m pip install pygame
```

## Como jogar

Execute o arquivo principal:

```bash
python game.py
```

No Windows, caso o `python` não seja reconhecido:

```bash
py game.py
```

## Controles

| Ação              | Tecla                     |
| ----------------- | ------------------------- |
| Mover à esquerda  | `←` ou `A`                |
| Mover à direita   | `→` ou `D`                |
| Pular / Pulo duplo| `Espaço`, `↑` ou `W`      |
| Reiniciar fase    | `R`                       |
| Sair              | `ESC`                     |

## Mecânicas

- **Pulo duplo:** você tem dois pulos disponíveis no ar, que são restaurados ao tocar uma plataforma.
- **Plataformas móveis (amarelas):** oscilam horizontal ou verticalmente. Cronometre o salto.
- **Espinhos:** te enviam de volta ao ponto de partida e incrementam o contador de mortes.
- **Queda no vazio:** cair fora da tela também conta como morte.
- **Meta:** alcance a bandeira vermelha no final do percurso para vencer.

## HUD

Durante a partida você vê no canto superior esquerdo:

- `Tempo` — cronômetro da run atual
- `Mortes` — quantas vezes você reapareceu no spawn
- `Pulos` — pulos disponíveis restantes no ar

## Estrutura do projeto

```
Game-python/
├── game.py      # Código principal do jogo
└── README.md
```

## Personalização

O arquivo `game.py` foi escrito para ser fácil de modificar:

- **Física:** ajuste `GRAVIDADE`, `FORCA_PULO` e `VELOCIDADE` no topo do arquivo.
- **Resolução:** mude `LARGURA` e `ALTURA`.
- **Cores:** todas as cores estão nomeadas como constantes (`AZUL_CEU`, `VERDE`, `LARANJA`, etc.).
- **Nova fase:** edite a função `criar_fase()` para adicionar, remover ou reposicionar `Plataforma`, `PlataformaMovel`, perigos e a meta.

## Licença

Projeto livre para fins educacionais e pessoais.
