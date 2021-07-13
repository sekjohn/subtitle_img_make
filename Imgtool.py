import io,os
import uuid
from pydantic import BaseModel, Field
from opyrator.components.types import FileContent
from PIL import Image
from pydantic.fields import T

class Fontcolor(str):
    black = "black"
    white = "white"

class DataInput(BaseModel):
    text: str = Field(
        ...,
        title="Text Input",
        description="The input text to use as basis to generate text.",
        max_length=1000,
    )
    image_file: FileContent = Field(..., mime_type="image")
    font_file: FileContent = Field(..., mime_type="font/opentype")
    Caption_x: int = Field(
        500,
        ge=0,
        le=1000,
        description="글씨 x 축 위치",
    )
    Caption_y: int= Field(
        500,
        ge=0,
        le=1000,
        description="글씨 y 축 위치",
    )
    auto_center: bool = Field(
        False,
        description="자동으로 x 축 센터를 맞춰 줍니다",
    )
    x_plus: int = Field(
        0,
        ge=0,
        description="좌표값 x 플러스(두번째 부터 적용)",
    )
    y_plus: int = Field(
        50,
        ge=0,
        description="좌표값 y 플러스(두번째 부터 적용)",
    )
    font_size: int = Field(
        55,
        ge=0,
        description="font size 조절",
    )
    font_color: Fontcolor = Field(Fontcolor.black, title="font color update 예정")

class DataOutput(BaseModel):
    generated_text: str = Field(...)
    json_data :str = Field(...)
    upscaled_image_file: FileContent = Field(
        ...,
        mime_type="image/png",
        description="변환 이미지",
    )
class Download:
    def img_download(data):
        try:
            img_url = f'img/{uuid.uuid4()}.png'
            Image.open(io.BytesIO(data.as_bytes())).save(img_url, format="PNG")
        except Exception as e:
            print(e)
            return False
        return img_url

    def font_download(data):
        try:
            font_url = f'font/{uuid.uuid4()}.otf'
            with open(font_url, mode="w+b") as f:
                f.write(data.as_bytes())
        except Exception as e:
            print(e)
        return font_url

class IMG:
    def __init__(self,data):
        self.txt_list = data['start']['txt_list']
        self.xy_plus = data['start']['xy_plus']
        self.xy_list = data['start']['xy_list']
        self.fonts_size = data['start']['fonts_size']
        self.fonts_color = data['start']['fonts_color']
        self.background_img_path = data['start']['background_img_path']
        self.fonts_path = data['start']['fonts_path']
        self.auto_center =  data['start']['auto_center']
    def text_xy_refine(self):
        text = self.txt_list
        x,y = self.xy_list
        pls_x,pls_y= self.xy_plus
        data_text = text.split("\n")
        xy_tuple = [(x,y)]

        for i in data_text:
            xy_tuple.append((x+pls_x,y+pls_y))
        return data_text,xy_tuple
        
    def Make_Imge(self):
        '''
        테스트 이미지 만들기
        '''
        from PIL import Image, ImageDraw, ImageFont
        try:
            im = Image.open(self.background_img_path)
            selectedFont =ImageFont.truetype(self.fonts_path,self.fonts_size) 
            draw = ImageDraw.Draw(im) #폰트경로과 사이즈를 설정해줍니다.
            txt_list,xy_list = self.text_xy_refine()

            for i,v in enumerate(txt_list):
                if self.auto_center:
                    x = im.size[0]
                    w ,h = ImageFont.truetype(self.fonts_path,self.fonts_size).getsize(txt_list[i]) 
                    draw.text(((x-w)/2,xy_list[i][1]/2),txt_list[i],font=selectedFont,fill=self.fonts_color)

                else:
                    draw.text(xy_list[i],txt_list[i],font=selectedFont,fill=self.fonts_color)

            img_byte_array = io.BytesIO()
            im.save(img_byte_array,format='png', subsampling=0, quality=100) 
            img_byte_array = img_byte_array.getvalue()
            print("img 반환 성공")
            if os.path.isfile(self.background_img_path) or os.path.isfile(self.fonts_path):
                file = [self.background_img_path,self.fonts_path]
                for i in file:
                    os.remove(i)
            return True, img_byte_array
        except Exception as e:
            print(e)
            
            return str(e)

def meta_dict_data(text,xy,xyplus,img_path,font_size,font_color,fonts_path,auto):
    try:
        json_data = {
            'start':{
                    'txt_list':text,
                    'xy_plus':xyplus,
                    'xy_list':xy,# 이미지에 텍스트가 고정될 좌표(예상),
                    'fonts_size':font_size,
                    'fonts_color':font_color,
                    'background_img_path':img_path,
                    'fonts_path': fonts_path,
                    'auto_center': auto
                
                }
        }
    except Exception as e:
        print(e)
    return json_data




def Lionlocket_Img_tool(input: DataInput) -> DataOutput:
    downlaod = Download
    img_url = downlaod.img_download(input.image_file)
    font_url = downlaod.font_download(input.font_file)

    make_setting = meta_dict_data(input.text,(input.Caption_x,input.Caption_y),(input.x_plus,input.y_plus),
        img_url,input.font_size,input.font_color,font_url,input.auto_center)

    img_class = IMG(make_setting)
    result,img_byte_array = img_class.Make_Imge()

    if result:
        result_text = "반환 성공"
    else:
        result_text = "반환 실패"
    return DataOutput(generated_text=result_text,upscaled_image_file=img_byte_array,json_data=str(make_setting))