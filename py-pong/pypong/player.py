import pygame, random, threading, Queue, serial

class BasicAIPlayer(object):
    def __init__(self):
        self.bias = random.random() - 0.5
        self.hit_count = 0
        
    def update(self, paddle, game):
        # Dead simple AI, waits until the ball is on its side of the screen then moves the paddle to intercept.
        # A bias is used to decide which edge of the paddle is going to be favored.
        if ((paddle.rect.x < game.bounds.centerx and game.ball.rect.x < game.bounds.centerx) or
            (paddle.rect.x > game.bounds.centerx and game.ball.rect.x > game.bounds.centerx)):
            delta = (paddle.rect.centery + self.bias * paddle.rect.height) - game.ball.rect.centery 
            if abs(delta) > paddle.velocity:
                if delta > 0:
                    paddle.direction = -1
                else:
                    paddle.direction = 1
            else:
                paddle.direction = 0
        else:
            paddle.direction = 0

    def hit(self):
        self.hit_count += 1
        if self.hit_count > 6:
            self.bias = random.random() - 0.5 # Recalculate our bias, this game is going on forever
            self.hit_count = 0
            
    def lost(self):
        # If we lose, randomise the bias again
        self.bias = random.random() - 0.5
        
    def won(self):
        pass
        
class KeyboardPlayer(object):
    def __init__(self, input_state, up_key=None, down_key=None):
        self.input_state = input_state
        self.up_key = up_key
        self.down_key = down_key
        
    def update(self, paddle, game):
        if self.input_state['key'][self.up_key]:
            paddle.direction = -1
        elif self.input_state['key'][self.down_key]:
            paddle.direction = 1
        else:
            paddle.direction = 0

    def hit(self):
        pass

    def lost(self):
        pass
        
    def won(self):
        pass
        
class MousePlayer(object):
    def __init__(self, input_state):
        self.input_state = input_state
        pygame.mouse.set_visible(False)
        
    def update(self, paddle, game):
        centery = paddle.rect.centery/int(paddle.velocity)
        mousey = self.input_state['mouse'][1]/int(paddle.velocity)
        if centery > mousey:
            paddle.direction = -1
        elif centery < mousey:
            paddle.direction = 1
        else:
            paddle.direction = 0

    def hit(self):
        pass

    def lost(self):
        pass

    def won(self):
        pass

class WheelPlayer(object):
    def __init__(self, port):
        self.port = port
        self.previous = None
        self.queue = Queue.Queue()
        self.threadRunning = False
        
        reader = threading.Thread(target=self.serialreader,
                                  args=(0, self.port))
        reader.start()
        
    def update(self, paddle, game):
        if self.threadRunning:
            while self.queue.qsize():
                try:
                    data = self.queue.get(0).strip()
                    print data

                    if data in ["R", "G", "B"]:
                        if self.previous != None:
                            rotation = self.rotate(self.previous, data)
                            print rotation
                            paddle.direction = rotation

                        self.previous = data
                except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                    pass
            
    def rotate(self, prev, curr):
        if ((prev == "G" and curr == "R") or
            (prev == "R" and curr == "B") or
            (prev == "B" and curr == "G")):
            return -5
        elif ((prev == "B" and curr == "R") or
              (prev == "R" and curr == "G") or
              (prev == "G" and curr == "B")):
            return 5
        else:
            return 0
            
    def serialreader(self, i, port):
        try:
            ser = serial.Serial(port, 9600)
        except serial.SerialException:
            print ("Couldn't open serial communication port (" +
                   port  + "), please check your connections.\n")
        else:
            print "Successfully started thread (" + port + ").\n"
            self.threadRunning = True
            while self.threadRunning:
                msg = ser.readline()
                self.queue.put(msg)

    def hit(self):
        pass

    def lost(self):
        pass

    def won(self):
        pass
