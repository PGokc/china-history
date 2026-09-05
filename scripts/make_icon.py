from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
im=Image.new('RGB',(1024,1024),(24,52,74));dr=ImageDraw.Draw(im)
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Songti.ttc',555)
dr.text((512,492),'明',font=font,fill=(245,242,236),anchor='mm')
dr.rectangle((755,755,807,855),fill=(122,47,53))
im.save(R/'App/Assets.xcassets/AppIcon.appiconset/AppIcon.png')
