#include <ESP8266WiFi.h>
#include <Servo.h>
#include <BlynkSimpleEsp8266.h>
#include <Adafruit_MLX90614.h>

const char* ssid = "TAPAS GHOSH";
const char* password = "sandy111102";
char auth[] = "nWr91tsDP7Xeo2froQrRwzXEiOc5Xku4"; //Enter your Blynk application auth token
char server2[] = "blynk-cloud.com";  // URL for Blynk Cloud Server
int port = 8080;

int x=-1;
int trig=0;
double temp_amb;
double temp_obj;

Servo myservo;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
WidgetLCD lcd(V2);

void setup() {
  WiFi.softAPdisconnect (true);
  Serial.begin(9600);
  delay(10);
  myservo.attach(D4);
  myservo.write(0);
  mlx.begin();  
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Blynk.config(auth, server2, port);
  Blynk.connect();
 Serial.print(WiFi.localIP());
  
}

BLYNK_WRITE(V0) {
  trig = param.asInt();
}

void loop() {
    
  Serial.println((String)"Trig:"+trig);
  
  if(Serial.available())
  {
   x = Serial.readString().toInt();
   lcd.clear();
  if(x==0)
  {
    lcd.print(0,0,"Sir please wear Mask");
    myservo.write(150);
    delay(2000);
    myservo.write(0);
  }
  Serial.println((String)"Mask:"+x);
  temp_amb = mlx.readAmbientTempC();
  temp_obj = mlx.readObjectTempC()-2.8;
  Serial.println((String)"Amb:"+temp_amb);
  Serial.println((String)"Temp:"+temp_obj);
  Blynk.virtualWrite(V1, temp_obj);
  lcd.clear();
  if(temp_obj<37.2)
     lcd.print(0,0,"Opening Gate");
  else
     lcd.print(0,0,"Temperature High");
  }
  Blynk.run();
}
