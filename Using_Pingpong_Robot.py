from pingpongthread import PingPongThread
from time import sleep
from keyboard import is_pressed

# 4개 로봇을 연결하는 인스턴스 생성.
PingPong = PingPongThread(number=4, group_id=46)
# 로봇 제어 쓰레드 시작.
PingPong.start()
# 모든 로봇이 연결될 때 까지 기다림.
PingPong.wait_until_full_connect()

# 웹캠 열기
PingPong.webcam_open(0)
#PingPong.webcam_open("http://192.168.66.1:9527/videostream.cgi?loginuse=admin&loginpas=admin")
# trainingData/trash_1 폴더 안에 '일반 쓰레기' 찍기.
PingPong.webcam_take_snapshots("trainingData/new_trash_1")
#PingPong.webcam_take_snapshots("trainingData/trash_1")

# trainingData/trash_2 폴더 안에 '플라스틱' 찍기.
#PingPong.webcam_take_snapshots("trainingData/trash_2")
PingPong.webcam_take_snapshots("trainingData/new_trash_2")

# trainingData/trash_3 폴더 안에 '종이' 찍기.
#PingPong.webcam_take_snapshots("trainingData/trash_3")
PingPong.webcam_take_snapshots("trainingData/new_trash_3")

# trainingData/track 폴더 안에 '경로' 찍기.
PingPong.webcam_take_snapshots("trainingData/track")

# 쓰레기 분류 및 경로 클래스 인스턴스 생성.
#normal = PingPongThread.ImageClass("normal", "trainingData/trash_1")
#plastic = PingPongThread.ImageClass("plastic", "trainingData/trash_2")
#paper = PingPongThread.ImageClass("paper", "trainingData/trash_3")
normal = PingPongThread.ImageClass("normal", "trainingData/new_trash_1")
plastic = PingPongThread.ImageClass("plastic", "trainingData/new_trash_2")
paper = PingPongThread.ImageClass("paper", "trainingData/new_trash_3")
track = PingPongThread.ImageClass("track", "trainingData/track")

# 모델 트레이닝.(학습 시키기)
# 첫 번째 인수는 저장하는 이름, 두 번째 인수는 knn 알고리즘의 k 값,
# 세 번째 인수는 모델 모드. 네 번째 인수 이후는 클래스 인스턴스들.
model = PingPong.train_classes("model/trashbot_model.json", 5, 1, normal, plastic, paper,track)

# 핑퐁 센서 수신 설정
PingPong.receive_sensor_data(1, method="periodic", period=0.5)
PingPong.receive_sensor_data(2, method="periodic", period=0.5)
PingPong.receive_sensor_data(3, method="periodic", period=0.5)
PingPong.receive_sensor_data(4, method="periodic", period=0.5)

# 버튼을 누르지 않으면 계속 반복하기
while not PingPong.get_current_button(1) == 1:
    # 현재 근접 센서값 출력
    print(PingPong.get_current_proxy(1))    
    # 0.5초 기다리기
    sleep(0.5)

#쓰레기가 일정 수준 이상 쌓였을 때, 3번 카메라 위치 변경(경로 탐색 모드)
while True:
    # 현재 근접 센서값 출력
    print(PingPong.get_current_proxy(1))  
    # 적외선 센서 값이 100보다 클 때
    if PingPong.get_current_proxy(1) > 100 : 
        print("경로 탐색 모드") 
        PingPong.run_motor_step(3,8,0.25)      #90도 회전
        sleep(0.25/8*60)
        break         # while 반복문 끝내기
    sleep(0.5)   # 0.5초 기다리기
# PingPong.run_motor([1,2,3,4],0)

# 프레임을 평가하는 인스턴스 생성. 누적 프레임은 1초 동안 보관.
frames_predictor = PingPong.FramesPredictor(model=model, timer_sec=3)

# 웹캠을 이용하여 객체를 인식하는 루프
# 쓰레기 분류 모드: 1,2번 로봇 제어로 입구 조정, 경로 탐색모드: 3,4번 제어로 경로 탐색
while not is_pressed('esc'):
    # 주피터 노트북 출력 비우기.(화면 초기화)
    PingPong.clear_output()
    # 현재 웹캠 프레임 가져오기.
    frame = PingPong.webcam_get_frame(window="Get_frame")
    # 현재 프레임을 평가.
    frames_prediction = frames_predictor.image_predict_and_accum(frame)
    print(frames_prediction)
    
    sleep(0.1) # 0.1초 기다리기.
    #가장 확률이 높은 클래스 이름을 max_class에 저장.
    max_class= max(frames_prediction, key=frames_prediction.get)
    if max_class == "normal" :
        print("일반 쓰레기입니다.")
        # 회전.
        PingPong.run_motor_step(1, 3, -40/360)
        sleep(40/360/3*60+5)
        PingPong.run_motor_step(1, 3, 40/360) # 원상 복구
        sleep(40/360/3*60+0.1)

    elif max_class == 'plastic':
        print("플라스틱입니다.")
        PingPong.run_motor_step(2, 3, -5/360)
        sleep(5/360/3*60+5)
        PingPong.run_motor_step(2, 3, 5/360)# 원상 복구
        sleep(5/360/3*60+0.1)
 
    elif max_class == 'paper':
        print("종이입니다.")
        PingPong.run_motor_step(1, 3, -10/360)
        sleep(10/360/3*60+5)
        PingPong.run_motor_step([1,2], 3, 10/360)
        sleep(10/360/3*60+0.1)
        
    elif max_class == 'track':
        print("경로를 탐색합니다.")
        PingPong.run_motor(4,15)
    else:
        PingPong.run_motor([1,2,3,4],0)
        #PingPong.run_motor([1,2,3,4],0)
    #PingPong.run_motor([1,2,3,4],0)

# 센서값 수신 종료
PingPong.stop_sensor_data(1)
PingPong.stop_sensor_data(2)
PingPong.stop_sensor_data(3)
PingPong.stop_sensor_data(4)
# 웹캠 종료
PingPong.webcam_close()
# 로봇 연결 종료
PingPong.end()