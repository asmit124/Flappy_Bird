import pygame
import neat
import time
import os
import random
pygame.font.init()

WIN_WIDTH=575
WIN_HEIGHT=800

GEN=0
VEL=5
score=0

BIRD_IMGS=[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]

PIPE_IMG=  pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG=  pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("imgs", "bg.png")), (WIN_WIDTH, WIN_HEIGHT))


STAT_FONT= pygame.font.SysFont("comicsans",50)


class Bird:
    IMGS=BIRD_IMGS
    MAX_ROTATION=25  #how much the bird will tilt
    ROT_VEL=20       #how fast it will rotate
    ANIMATION_TIME=5 #how fast the bird will flap its wing

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0         #initially the tilt is 0
        self.tick_count =0  #physics of the bird while jumping or falling down
        self.vel=0          #since not moving initially
        self.height=self.y
        self.img_count=0    #which image we are curretly showing for the bird
        self.img=self.IMGS[0] #references bird images

    def jump(self):
        self.vel= -10.5 #negative vel => upwards
        self.tick_count=0 #keep track of when we last jumped
        self.height=self.y #where the bird originally started moving from

    def move(self):
        self.tick_count+=1 #a tick happened

        d=self.vel*self.tick_count + 1.5*self.tick_count**2 #displacement =>how many pixels we are movig up or down
        #s = ut + 1/2 at2
        #self.tick_count =>how many seconds we have been moving forward for since we last jumped
        #-10.5 * 1 +1.5*1*1 = -9 => in this frame we are moving 9 pixels upwards

        if d>=16:
            d=16
        
        if d<0:
            d-=2 #if we are moving upwards we jump a little more

        self.y=self.y+d #add d to our current y position

        if d<0 or self.y < self.height + 50: #if bird position is above jump position
            if self.tilt < self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION #tilt upwards
        else: 
            if self.tilt > -90:     #tilt downwards
                self.tilt-= self.ROT_VEL #tilts downward while falling
            
    def draw(self,win):
        self.img_count+=1
        #what image we should show based on the current image count
        if self.img_count <= self.ANIMATION_TIME:
            self.img=self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2: 
            self.img=self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3: 
            self.img=self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4: 
            self.img=self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 +1: 
            self.img=self.IMGS[0] 
            self.img_count=0       

        if self.tilt<=-80: #when tilt angle approaches 90 degrees we dont want the bird to flap 
            #its wings
            self.img=self.IMGS[1]
            self.img_count=self.ANIMATION_TIME*2 #if it jumps back up it shouldn't skip a frame


        rotated_image=pygame.transform.rotate(self.img,self.tilt)
        #we need to rotate the image around the centre
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft) # draw the image on the window
        #blit=>draw

    #collision
    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Pipe:
    GAP=200 #vertical space between pipes
    global VEL
    VEL=5+0.1*score*score  #velocity with which the pipe is moving(bird doesnt move forward)

    def __init__(self, x):
        self.x=x
        self.height=0

        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False,True) #we need to flip the pipe for 
        #top layer
        self.PIPE_BOTTOM=PIPE_IMG

        self.passed=False  #if the bird has already passed by this pipe
        self.set_height()  #how tall the pipe is 

    def set_height(self):
        self.height=random.randrange(50,450) #range between 50 to 450
        self.top=self.height - self.PIPE_TOP.get_height()
        #imagine we want to place a inverted pipe
        #we have the height of the lower face and we want to know the location/height 
        #of the base so height of base/top= known height - height of pipe
        self.bottom=self.height+self.GAP #place the bottom pipes
       # self.height: The height of the upper pipe.
       # self.GAP: The space between the upper and lower pipes.
       # self.bottom: The Y-coordinate of the bottom edge of the lower pipe.

    def move(self):
        self.x-=VEL #move the pipe left with a velocity

    def draw(self,win): 
        win.blit(self.PIPE_TOP,(self.x,self.top))   
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))  


#get_mask is used for pixel-perfect collision detection by creating a binary mask of game objects like the bird and pipes.
#This avoids false positives from bounding box collisions by only checking the non-transparent parts of objects.

#Instead of relying on rectangular boundaries, which can cause inaccuracies, get_mask creates a mask where each pixel is either "1" (object) or "0" (background).
#This enables more precise collision detection between objects like the bird and pipes.

#Masks are generated from the images of the bird and pipes. 
# By comparing these masks at the pixel level, collisions are detected only when the visible parts of the objects overlap. This ensures accuracy in collision detection.

    def collide(self,bird):
        bird_mask= bird.get_mask()
        top_mask= pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x,self.top-round(bird.y)) #offset from the bird to top mask
        bottom_offset = (self.x - bird.x,self.bottom-round(bird.y))

        #find out if these masks collide
        b_point=bird_mask.overlap(bottom_mask,bottom_offset) #point of collision bw bottom pipe and bird mask
        #returns none if no collision
        t_point=bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        
        return False

class Base:
    global VEL
    VEL=5+score*score
    WIDTH=BASE_IMG.get_width()
    IMG=BASE_IMG

    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH

#we use two bases kept adjacent to each other 
#as soon as the front base leaves the window the rear base takes its place and
#the front base moves in the rear position and this is repeated
    def move(self):
        self.x1-=VEL
        self.x2-=VEL

        if self.x1+self.WIDTH < 0: # condition to check it it is completely off the screen
            self.x1=self.x2+self.WIDTH #cycle it back

        if self.x2+self.WIDTH < 0:
            self.x2=self.x1+self.WIDTH

        
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))
  
    
def draw_window(win,birds,pipes,base,score,gen):
    win.blit(BG_IMG,(0,0)) #draw the background img on the window (0,0) =>top left cordinate of the image
    for pipe in pipes:
        pipe.draw(win)
    
    text=STAT_FONT.render("Score: "+str(score),1,(255,255,255))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))

    text=STAT_FONT.render("Gen: "+str(gen),1,(255,255,255))
    win.blit(text,(10,10))

    base.draw(win) 

    for bird in birds:
        bird.draw(win)
        #insert bird in window
    pygame.display.update() #updates and refreshes the display

def main(genomes,config):
    global GEN
    GEN+=1
    nets=[]
    ge=[]
    birds=[] #starting position of bird

    for _, g in genomes: # since genomes is a tuple
        net=neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        g.fitness=0
        ge.append(g)

    base=Base(730)
    pipes=[Pipe(600)]
    win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT)) #create the window
    clock=pygame.time.Clock()
    run=True
    global score
    global VEL
    score=0
    VEL=5

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                run=False
                break
                pygame.quit()  
                quit()   


        pipe_ind=0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind=1 #if we pass a pipe then move to the next pipe
        
        else:#no birds left 
            run=False
            break


        for x,bird in enumerate(birds):
            bird.move()
            ge[x].fitness+=0.1

            output=nets[x].activate((bird.y,abs(bird.y-pipes[pipe_ind].height),abs(bird.y-pipes[pipe_ind].bottom)))
            
            if output[0]> 0.5 :
                bird.jump()

        #bird.move()  
        add_pipe = False
        rem=[]
        for pipe in pipes:
            for x,bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness-=1 #everytime a bird hits a pipe
                    #its fitness score is decreased
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
            
                if not pipe.passed and pipe.x < bird.x: #checks if the bird has passed the pipe
                    #if passed then we generate a new pipe
                    pipe.passed=True
                    add_pipe=True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # pipe is completely off the screen
                rem.append(pipe) #we need to remove the pipe

            pipe.move()

        if add_pipe:
            score+=1
            VEL+=0.125
            for g in ge:
                g.fitness+=5 # if it doesnt collide we increase
                #its fitness score by 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)
        
        for x,bird in enumerate(birds):
            if bird.y+ bird.img.get_height()>=730 or bird.y < 0: #bird hits the floor or if it gets above the screen
                #and never die
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        

        base.move()
        draw_window(win,birds,pipes,base,score,GEN)  


def run(config_path):
    config=neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                              neat.DefaultSpeciesSet,neat.DefaultStagnation,
                              config_path)
    
    # define all the headings in NEAT

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)


if __name__=="__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)