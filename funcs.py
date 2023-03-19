import random

### Random name for user photo
def random_img_name():
    name_list = list()

    for i in range(1, 15):
        name_list.append(random.randint(97, 122))

    for i in range(1, 5):
        name_list.append(random.randint(48, 57))

    name_list = [chr(i) for i in name_list]

    return "{}.jpg".format("".join(name_list))

### We clear the user text from the /get_answer command
def clean_text(text):
    txt_list = [i for i in text.split(" ") if i != "/get_answer"]
    return " ".join(txt_list)


