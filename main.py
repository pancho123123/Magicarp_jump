import pygame

WIDTH = 960
HEIGHT = 540

BLACK = (0, 0, 0)
WHITE = ( 255, 255, 255)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

def draw_text(surface, text, size, x, y, color):
    font = pygame.font.SysFont("serif", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


class Player(pygame.sprite.Sprite):
    def __init__(self,num,tecla_salto,counter_obj):
        super().__init__()
        self.num = num
        self.image_quieto = pygame.transform.scale(pygame.image.load("img/player.png"),(149,50))
        self.image = self.image_quieto
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        if num == 1:
            self.rect.x = WIDTH//4//2
        elif num == 2:
            self.rect.x = WIDTH//4 + WIDTH//4//2 - 35
        elif num == 3:
            self.rect.x = WIDTH//2 + WIDTH//4//2 -self.image.get_width()//2
        else:
            self.rect.x = WIDTH - WIDTH//4//2 -self.image.get_width()//2 - 35
        self.rect.y = HEIGHT - 99
        self.anim_subida = []
        for i in range(1,15):
            img = pygame.image.load(f"img/jump/1/{i}.png")
            img = pygame.transform.scale(img,(149,117))
            img.set_colorkey(WHITE)
            self.anim_subida.append(img)
        self.anim_caida = []
        for i in range(15,25):
            img = pygame.image.load(f"img/jump/2/{i}.png")
            img = pygame.transform.scale(img,(150,115))
            img.set_colorkey(WHITE)
            self.anim_caida.append(img)
        self.counter = counter_obj
        self.tecla_salto = tecla_salto
        self.vy = 0
        self.gravity = 0.98
        self.fuerza_salto = -29
        self.fuerza_perfecto = -35
        self.en_suelo = True
        self.tiempo_en_suelo = 0
        self.VENTANA_PERFECTO = 15
        self.esta_presionando_salto = False
        self.esta_presionado = False
        self.altura_meta = 150
        self.ya_sumo_este_salto = False
        self.estado = "quieto"
        self.frame = 0
        self.frame_timer = 0

    def handle_input(self, teclas):
        presionando_ahora = teclas[self.tecla_salto]
        if presionando_ahora and not self.esta_presionado and self.rect.y > HEIGHT - 124:
            if self.tiempo_en_suelo < self.VENTANA_PERFECTO:
                self.vy = self.fuerza_perfecto
            else:
                self.vy = self.fuerza_salto
            
            self.en_suelo = False
            self.tiempo_en_suelo = 999
            self.ya_sumo_este_salto = False
        
        if not presionando_ahora and self.esta_presionado and not self.en_suelo and self.vy < 0:
            self.vy *= 0.55
        self.esta_presionado = presionando_ahora

    def update(self):
        if self.en_suelo:
            self.vy = 0
            self.rect.y = HEIGHT - 99
            self.image = self.image_quieto
            self.estado = "quieto"
            self.frame = 0
            self.tiempo_en_suelo += 1
            return   
        self.vy += 0.98  # gravedad
        self.rect.y += self.vy

        self.frame_timer += 1
        nuevo_estado = "subiendo" if self.vy < 0 else "cayendo"
        if nuevo_estado != self.estado:
            self.estado = nuevo_estado
            self.frame = 0
        if self.frame_timer % 5 == 0:
            self.frame += 1
        if self.estado == "subiendo":
            self.frame %= len(self.anim_subida)
            self.image = self.anim_subida[self.frame]
        else:
            self.frame %= len(self.anim_caida)
            self.image = self.anim_caida[self.frame]
        if self.rect.y < self.altura_meta:
            if not self.ya_sumo_este_salto:
                self.counter.sumar_puntos()
                self.ya_sumo_este_salto = True
            self.vy += 8
            
        if self.rect.y >= HEIGHT - 99:
            self.rect.y = HEIGHT - 99

            self.vy = 0
            if not self.en_suelo:
                self.tiempo_en_suelo = 0
            self.en_suelo = True            
            self.ya_sumo_este_salto = False



class Counter(pygame.sprite.Sprite):
    def __init__(self,num):
        super().__init__()
        self.num = num
        self.image = count_img[num -1]
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        if num == 1:        
            self.rect.x = WIDTH//4//2 - 34
        elif num == 2:
            self.rect.x = WIDTH//4 + WIDTH//4//2 - 66
        elif num == 3:
            self.rect.x = WIDTH//2 + WIDTH//4//2 -self.image.get_width()//2 - 15
        else:
            self.rect.x = WIDTH - WIDTH//4//2 -self.image.get_width()//2 -46
        self.rect.y = 0
        self.base_y = self.rect.y
        
        self.anim_golpe = self.cargar(f"img/counter/{num}",13,(160,155))
        self.frame_golpe = 0
        self.golpeando = False

        self.numbers_anim = []
        for n in range(10):
            self.numbers_anim.append(self.cargar(f"img/number/{n}",8,(34,25)))
        self.score = 0
        self.actualizar_digitos(forzar_anim=False)
        
        self.digitos = [0] # empieza en 0

    def actualizar_digitos(self,forzar_anim = False):
        texto = f"{self.score:03d}" #3 digitos
        nuevo_digitos = [int(d) for d in texto]         
        self.anim_digitos = []
        for dig in nuevo_digitos:
            self.anim_digitos.append({
'valor':dig,
'frame':0 if forzar_anim else 10,
'animando':forzar_anim
})
        self.digitos = nuevo_digitos
    def cargar(self, carpeta, nu,escala=(160,155)):
        anim = []
        for i in range(1,nu):
            img = pygame.image.load(f"{carpeta}/{i}.png").convert()
            img.set_colorkey(WHITE)
            anim.append(pygame.transform.scale(img,escala))
        return anim

    def sumar_puntos(self):
        self.score += 1
        self.golpeando = True
        self.frame_golpe = 0
        self.actualizar_digitos(forzar_anim=True)
        

    def update(self):
        if self.golpeando:
            self.frame_golpe += 1
            if self.frame_golpe >= len(self.anim_golpe):
                self.frame_golpe = 0
                self.golpeando = False

        for d in self.anim_digitos:
            if d['animando']:
                d['frame'] += 1
                if d['frame'] >= 6:
                    d['frame'] = 6 # se queda en el ultimo frame
                    d['animando'] = False

    def draw(self,screen):
        offset_y = 0
        if self.golpeando:
            # hace que suba 20 pixeles y baje, usa el frame como curva
            offset_y = -20 * (1-abs(self.frame_golpe - 5)/5)
        screen.blit(self.anim_golpe[self.frame_golpe],(self.rect.x,self.base_y + offset_y))

        ANCHO = 35
        X_BASE = self.rect.left + 28
        #total_digitos = len(self.anim_digitos)

        for i, d in enumerate(self.anim_digitos):
            frame = min(d['frame'], len(self.numbers_anim[d['valor']])-1)
            img_num = self.numbers_anim[d['valor']][frame]
            #si tu score es 12 dibuja 1 en x , 2 en x + 50
            screen.blit(img_num,(X_BASE + i*ANCHO,self.base_y + offset_y + 45))

count_img = []
count_list = ["img/count1.png","img/count2.png","img/count3.png","img/count4.png"]
for img in count_list:
    count_img.append(pygame.transform.scale(pygame.image.load(img),(160,155)))

#counter1_anim = []
#for i in range(11):
#    file = "img/counter/1/{}.png".format(i)
#    img = pygame.image.load(file).convert()
#    img.set_colorkey(WHITE)
#    img_scale = pygame.transform.scale(img, (160,155))
#    counter1_anim.append(img_scale)



go_img = pygame.transform.scale(pygame.image.load("img/go.png"),(212,150))
go1_img = pygame.transform.scale(pygame.image.load("img/1go.png"),(91,159))
go2_img = pygame.transform.scale(pygame.image.load("img/2go.png"),(120,159))
go3_img = pygame.transform.scale(pygame.image.load("img/3go.png"),(116,159))
fond = pygame.transform.scale(pygame.image.load("img/fond.png"),(960,540))
p3p_img = pygame.transform.scale(pygame.image.load("img/3p.png"),(80,50))
p3p_img.set_colorkey(WHITE)
p4p_img = pygame.transform.scale(pygame.image.load("img/4p.png"),(89,50))
p4p_img.set_colorkey(WHITE)

all_sprites = pygame.sprite.Group()
counters = []
for i in range(1,5):
    counter = Counter(i)
    all_sprites.add(counter)
    counters.append(counter)
players = pygame.sprite.Group()
player1 = Player(1,pygame.K_q,counters[0])
player2 = Player(2,pygame.K_r,counters[1])
player3 = Player(3,pygame.K_u,counters[2])
player4 = Player(4,pygame.K_l,counters[3])

all_sprites.add(player1,player2,player3,player4)
players.add(player1,player2,player3,player4)
start_time = 0


running = True
while running:
    now = pygame.time.get_ticks()
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    teclas = pygame.key.get_pressed()           
    if now - start_time >= 21000:
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        start_time = pygame.time.get_ticks()
                        for c in counters:
                            c.score = 0
                            c.frame_golpe = 0
                            c.golpeando = False
                            c.actualizar_digitos(forzar_anim=False)
                        for p in players:
                            p.rect.y = 100
                        
    screen.fill(BLACK)
    screen.blit(fond,(0,0))
    screen.blit(p3p_img,(480,HEIGHT-58))
    screen.blit(p4p_img,(684,HEIGHT-58))
    for p in players:
        p.handle_input(teclas)
    all_sprites.update()
    all_sprites.draw(screen)
    for c in counters:
        c.update()
        c.draw(screen)
    pygame.display.flip()
