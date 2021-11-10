from bot import Botmail
import cv2
from datetime import datetime


bot = Botmail(bot='Mybot_email.com', master='Master_email.com')


class Actions:
    """
    #Sending Intuders PIC with current location
    """
    current_date = datetime.now()
    raw_name = f"img-{current_date}.jpg"
    path = f"IPICS/{raw_name}"

    def click_Photo(self):
        camera_port = 0
        ramp_frames = 30
        camera = cv2.VideoCapture(camera_port)

        def get_image():
            retval, im = camera.read()
            return im

        for i in range(ramp_frames):
            temp = camera.read()

        camera_capture = get_image()

        cv2.imwrite(f"{self.path}", camera_capture)
        del(camera)

        bot.send_mail(file_name=self.path)

        return 1

    def ShutDown(self):
        """
        # Shutting down Machine
        """
        os.system("shutdown now -h")

        return 1

    def LogOut(self):
        """
        # LogOut
        """
        pass


UTILS = Actions()

def main():

    data = bot.get_code()
    ACTION_CODE = data["ACTION_CODE"]

    if ACTION_CODE == "7777":

        UTILS.click_Photo()
        print(
            f"Intrudrs images sent to {bot.master} ....Please chek your Email \n")

    elif ACTION_CODE == "0000":
        UTILS.ShutDown()
        print("Shutting down")

    else:
        print(f" {ACTION_CODE} Not an action code ")


if __name__ == '__main__':
    main()
