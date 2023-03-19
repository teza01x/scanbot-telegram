import cv2
import pytesseract
from config import tesseract_path, tesseract_cfg, token_limit


def text_detect(image):
	### Path to tesseract
	pytesseract.pytesseract.tesseract_cmd = tesseract_path

	### Image calibrate
	img = cv2.imread(image)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	config = tesseract_cfg

	### Get text from image
	text = pytesseract.image_to_string(img, config=config)

	if len(text) <= 750:
		### Send request to openai for answer
		return text

	return f"⛔️ERROR⛔️\nYour text has exceeded the allowed word limit. Set limit is {token_limit} words/per query."


def text_edit(text):
	### Generating a list from the text in the picture
	start_list = text.split("\n")
	start_list = [i for i in start_list if len(i) > 0]

	### Removing single letters/characters at the beginning of lines
	pre_finish_list = list()
	for i in start_list:
		if (i[0] in "O" and len(i) < 2) or (i[0] in "O" and i[1] in " ") or (i[0] in "©"):
			pre_finish_list.append(i[1:])
		else:
			pre_finish_list.append(i)

	### Deleting strings consisting only of special characters
	finish_list = list()
	count = 0
	for i in pre_finish_list:
		for j in i:
			if 97 <= ord(j.lower()) <= 122:
				count += 1
			elif 48 <= ord(j.lower()) <= 57:
				count += 1
		if count > 0:
			finish_list.append(i)
			count = 0

	### Sending a finished line of text
	return "\n".join(finish_list)

