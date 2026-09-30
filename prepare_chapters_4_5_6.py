#!/usr/bin/env python3
"""
Prepares 16:9 Balanced Images and JSON scripts for:
- Chapter 4: Người Trộm Điều (16 scenes)
- Chapter 5: Đám Cỏ Đậu (12 scenes)
- Chapter 6: Chuyện Ly Nước (16 scenes)
"""

import os
import json
from PIL import Image

def make_16x9_balanced(input_path, out_path, focus_box=None):
    if not os.path.exists(input_path):
        print(f"[!] File not found: {input_path}")
        return
    im = Image.open(input_path).convert('RGB')
    w, h = im.size
    if focus_box:
        x1, y1, x2, y2 = [int(v * dim) for v, dim in zip(focus_box, [w, h, w, h])]
        cropped = im.crop((x1, y1, x2, y2))
    else:
        cropped = im
    cw, ch = cropped.size
    target_ratio = 16.0 / 9.0
    curr_ratio = cw / ch
    if curr_ratio > target_ratio:
        new_w = int(ch * target_ratio)
        offset = (cw - new_w) // 2
        final_crop = cropped.crop((offset, 0, offset + new_w, ch))
    else:
        new_h = int(cw / target_ratio)
        offset = (ch - new_h) // 2
        final_crop = cropped.crop((0, offset, cw, offset + new_h))
    res = final_crop.resize((1920, 1080), Image.Resampling.LANCZOS)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    res.save(out_path, quality=95)
    print(f"Created: {out_path}")

def generate_chapter_4():
    # Chapter 4: Người Trộm Điều (16 scenes)
    crops = [
        ("s4_01_cashew_orchard.jpg", "page_38_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s4_02_cashew_fruit.jpg", "page_38_Im1.jpg", (0.1, 0.1, 0.9, 0.9)),
        ("s4_03_stolen_cashew.jpg", "page_39_Im2.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s4_04_monk_night_walk.jpg", "page_40_Im0.jpg", (0.0, 0.0, 0.8, 1.0)),
        ("s4_05_monk_calm.jpg", "page_40_Im0.jpg", (0.2, 0.2, 0.7, 0.95)),
        ("s4_06_novice_wakes.jpg", "page_41_Im1.jpg", (0.1, 0.1, 0.9, 0.95)),
        ("s4_07_novice_finds_monk.jpg", "page_42_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s4_08_monk_comforts_novice.jpg", "page_43_Im1.jpg", (0.1, 0.1, 0.9, 0.95)),
        ("s4_09_moonlit_night.jpg", "page_44_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s4_10_thieves_rustling.jpg", "page_45_Im0.jpg", (0.0, 0.0, 0.9, 1.0)),
        ("s4_11_monk_prevents_stone.jpg", "page_45_Im0.jpg", (0.25, 0.1, 0.85, 0.95)),
        ("s4_12_approaching_tree.jpg", "page_46_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s4_13_children_scared.jpg", "page_46_Im0.jpg", (0.3, 0.2, 0.95, 0.95)),
        ("s4_14_monk_gentle_call.jpg", "page_47_Im1.jpg", (0.0, 0.0, 0.8, 1.0)),
        ("s4_15_teaching_generosity.jpg", "page_47_Im1.jpg", (0.15, 0.1, 0.95, 0.95)),
        ("s4_16_moral_lesson.jpg", "page_48_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
    ]
    for out_name, in_name, box in crops:
        make_16x9_balanced(f"data/book_illustrations/{in_name}", f"data/book_illustrations/{out_name}", box)

    script_c4 = {
        "title": "Chương 4: Người Trộm Điều",
        "description": "Bài học sâu sắc về đức ly tham và lòng thương yêu tha thứ của Đức Trưởng lão Thích Thông Lạc tại Chùa Am.",
        "scenes": [
            {
                "scene_id": "scene_01",
                "text": "Trước đây, Chùa Am đất rộng thênh thang, Thầy đã tự tay vun trồng hơn một trăm gốc điều sum sê tươi tốt.",
                "image_file": "data/book_illustrations/s4_01_cashew_orchard.jpg"
            },
            {
                "scene_id": "scene_02",
                "text": "Đến mùa thu hoạch, khắp vườn trĩu nặng từng chùm quả mọng, tỏa hương thơm ngát và mang lại hạt điều béo bùi.",
                "image_file": "data/book_illustrations/s4_02_cashew_fruit.jpg"
            },
            {
                "scene_id": "scene_03",
                "text": "Vào những đêm thanh vắng, có người hay lẻn vào bẻ trộm hạt điều, bỏ lại xác quả vương vãi khắp gốc cây.",
                "image_file": "data/book_illustrations/s4_03_stolen_cashew.jpg"
            },
            {
                "scene_id": "scene_04",
                "text": "Buổi tối Thầy thường ngủ rất ít, nửa đêm thức giấc, Thầy lặng lẽ ra ngồi tĩnh tọa hoặc tản bộ dưới rặng điều xanh.",
                "image_file": "data/book_illustrations/s4_04_monk_night_walk.jpg"
            },
            {
                "scene_id": "scene_05",
                "text": "Biết rõ có người vào bẻ trộm, nhưng Thầy chẳng một lời trách móc, cũng không bao giờ rình rập để bắt bớ ai.",
                "image_file": "data/book_illustrations/s4_05_monk_calm.jpg"
            },
            {
                "scene_id": "scene_06",
                "text": "Đêm ấy, Chú Tiểu ngủ chung thất chợt giật mình tỉnh giấc, nhìn quanh không thấy bóng dáng Thầy đâu.",
                "image_file": "data/book_illustrations/s4_06_novice_wakes.jpg"
            },
            {
                "scene_id": "scene_07",
                "text": "Chú bước vội ra sân, thấy Thầy đang đứng trầm ngâm, đôi mắt hướng nhìn về khoảng trời đêm bao la tĩnh mịch.",
                "image_file": "data/book_illustrations/s4_07_novice_finds_monk.jpg"
            },
            {
                "scene_id": "scene_08",
                "text": "Thầy dịu dàng xoa đầu Chú Tiểu và bảo: Thầy già ít ngủ ra hóng mát, con còn nhỏ hãy mau vào ngủ cho lại sức.",
                "image_file": "data/book_illustrations/s4_08_monk_comforts_novice.jpg"
            },
            {
                "scene_id": "scene_09",
                "text": "Chú Tiểu tha thiết xin được thức cùng Thầy dưới ánh trăng non đầu tháng, nghe gió thoảng hương điều bình yên.",
                "image_file": "data/book_illustrations/s4_09_moonlit_night.jpg"
            },
            {
                "scene_id": "scene_10",
                "text": "Chợt nghe tiếng cành cây xào xạc trong vườn, Chú Tiểu liền tính nhặt đá ném sang để đuổi kẻ trộm chạy mất.",
                "image_file": "data/book_illustrations/s4_10_thieves_rustling.jpg"
            },
            {
                "scene_id": "scene_11",
                "text": "Thầy vội ngăn lại: Đừng làm vậy con! Lỡ họ hoảng sợ té ngã thì nguy hiểm tính mạng, vì nghèo túng nên họ mới làm liều.",
                "image_file": "data/book_illustrations/s4_11_monk_prevents_stone.jpg"
            },
            {
                "scene_id": "scene_12",
                "text": "Hai Thầy trò nhẹ bước tới gần, trông thấy mấy đứa trẻ xóm nghèo đang ngồi vắt vẻo trên ngọn cây điều.",
                "image_file": "data/book_illustrations/s4_12_approaching_tree.jpg"
            },
            {
                "scene_id": "scene_13",
                "text": "Trông thấy bóng Thầy, lũ trẻ hồn xiêu phách lạc, luống cuống định nhảy vội xuống đất để bỏ chạy thoát thân.",
                "image_file": "data/book_illustrations/s4_13_children_scared.jpg"
            },
            {
                "scene_id": "scene_14",
                "text": "Thầy liền cất tiếng hiền từ: Các con đừng sợ, Thầy không la mắng đâu, cứ từ từ trèo xuống kẻo ngã đau.",
                "image_file": "data/book_illustrations/s4_14_monk_gentle_call.jpg"
            },
            {
                "scene_id": "scene_15",
                "text": "Thầy ân cần căn dặn: Đừng đi hái trộm nguy hiểm nữa, mai này muốn ăn cứ đến xin, Thầy sẽ hoan hỷ cho các con.",
                "image_file": "data/book_illustrations/s4_15_teaching_generosity.jpg"
            },
            {
                "scene_id": "scene_16",
                "text": "Vườn điều xưa nay đã già cỗi theo tháng năm, nhưng đức tính ly tham và tình thương tha thứ của Thầy mãi soi sáng muôn đời.",
                "image_file": "data/book_illustrations/s4_16_moral_lesson.jpg"
            }
        ]
    }
    with open("data/chapters/chapter4_script.json", "w", encoding="utf-8") as f:
        json.dump(script_c4, f, ensure_ascii=False, indent=2)
    print("Chapter 4 script saved!")

def generate_chapter_5():
    # Chapter 5: Đám Cỏ Đậu (12 scenes)
    crops = [
        ("s5_01_monk_peaceful.jpg", "page_49_Im1.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s5_02_monk_walking.jpg", "page_50_Im0.jpg", (0.0, 0.0, 0.8, 1.0)),
        ("s5_03_students_rejoice.jpg", "page_50_Im0.jpg", (0.35, 0.1, 0.95, 0.95)),
        ("s5_04_following_monk.jpg", "page_51_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s5_05_orchard_ground.jpg", "page_51_Im0.jpg", (0.1, 0.1, 0.9, 0.95)),
        ("s5_06_peanut_grass.jpg", "page_52_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s5_07_fallen_leaf.jpg", "page_52_Im0.jpg", (0.2, 0.2, 0.85, 0.95)),
        ("s5_08_monk_bends_down.jpg", "page_53_Im0.jpg", (0.0, 0.0, 0.9, 1.0)),
        ("s5_09_monk_teaching_leaf.jpg", "page_53_Im0.jpg", (0.25, 0.1, 0.95, 0.95)),
        ("s5_10_moving_leaf.jpg", "page_54_Im0.jpg", (0.0, 0.0, 0.85, 1.0)),
        ("s5_11_students_realization.jpg", "page_54_Im0.jpg", (0.25, 0.1, 0.95, 0.95)),
        ("s5_12_infinite_love.jpg", "page_55_Im1.jpg", (0.0, 0.0, 1.0, 1.0)),
    ]
    for out_name, in_name, box in crops:
        make_16x9_balanced(f"data/book_illustrations/{in_name}", f"data/book_illustrations/{out_name}", box)

    script_c5 = {
        "title": "Chương 5: Đám Cỏ Đậu",
        "description": "Bài học xúc động về đức hiếu sinh thương yêu cỏ cây từ hành động nhặt lá đu đủ của Đức Trưởng lão.",
        "scenes": [
            {
                "scene_id": "scene_01",
                "text": "Hai năm trước ngày nhập diệt, Thầy dành trọn thời gian tĩnh dưỡng, an trú trong sự thanh tịnh nhiệm màu của chánh niệm.",
                "image_file": "data/book_illustrations/s5_01_monk_peaceful.jpg"
            },
            {
                "scene_id": "scene_02",
                "text": "Vào một buổi chiều êm ả, Thầy thong dong tản bộ một vòng quanh khuôn viên tu viện cùng hai người đệ tử thân cận.",
                "image_file": "data/book_illustrations/s5_02_monk_walking.jpg"
            },
            {
                "scene_id": "scene_03",
                "text": "Khi đi ngang qua bếp, các học trò trong ban đời sống trông thấy Thầy thì mừng rỡ ùa ra kính cẩn xá chào.",
                "image_file": "data/book_illustrations/s5_03_students_rejoice.jpg"
            },
            {
                "scene_id": "scene_04",
                "text": "Đoàn học trò hân hoan rảo bước nối theo sau từng bước chân khoan thai, đong đầy từ bi ấm áp của Người.",
                "image_file": "data/book_illustrations/s5_04_following_monk.jpg"
            },
            {
                "scene_id": "scene_05",
                "text": "Thầy dừng chân bên mảnh vườn rợp bóng xà cừ và đu đủ, nơi tu viện đã dày công chăm sóc để tạo cảnh quan xanh sạch.",
                "image_file": "data/book_illustrations/s5_05_orchard_ground.jpg"
            },
            {
                "scene_id": "scene_06",
                "text": "Dưới tán cây râm mát, thảm cỏ đậu mọc lên non mượt, nở những đóa hoa vàng li ti rạng rỡ chào đón nắng chiều.",
                "image_file": "data/book_illustrations/s5_06_peanut_grass.jpg"
            },
            {
                "scene_id": "scene_07",
                "text": "Chợt trên nền thảm cỏ xanh mướt, một nhành lá đu đủ khô to lớn vừa lìa cành nằm đè nặng lên những mầm non.",
                "image_file": "data/book_illustrations/s5_07_fallen_leaf.jpg"
            },
            {
                "scene_id": "scene_08",
                "text": "Trông thấy cảnh tượng ấy, Thầy liền cúi người xuống, nâng niu nhấc chiếc lá đu đủ nặng trĩu ra khỏi thảm cỏ.",
                "image_file": "data/book_illustrations/s5_08_monk_bends_down.jpg"
            },
            {
                "scene_id": "scene_09",
                "text": "Thầy quay lại ôn tồn nhắc nhở: Chiếc lá lớn thế này đè lên, cỏ non bên dưới sẽ bị nghẹt thở và rất khó lòng mọc được.",
                "image_file": "data/book_illustrations/s5_09_monk_teaching_leaf.jpg"
            },
            {
                "scene_id": "scene_10",
                "text": "Thầy nhẹ nhàng đặt cành lá sang một góc đất trống rồi lại mỉm cười, tiếp tục dạo bước trong sự thanh thản.",
                "image_file": "data/book_illustrations/s5_10_moving_leaf.jpg"
            },
            {
                "scene_id": "scene_11",
                "text": "Hành động nhỏ bé của Thầy khiến các đệ tử bừng tỉnh, nhận ra bấy lâu nay con người thường quá thờ ơ với muôn loài.",
                "image_file": "data/book_illustrations/s5_11_students_realization.jpg"
            },
            {
                "scene_id": "scene_12",
                "text": "Đó chính là bài học không lời vô giá về lòng từ bi, biết trân trọng và bảo bọc sinh mệnh của từng ngọn cỏ lá cây.",
                "image_file": "data/book_illustrations/s5_12_infinite_love.jpg"
            }
        ]
    }
    with open("data/chapters/chapter5_script.json", "w", encoding="utf-8") as f:
        json.dump(script_c5, f, ensure_ascii=False, indent=2)
    print("Chapter 5 script saved!")

def generate_chapter_6():
    # Chapter 6: Chuyện Ly Nước (16 scenes)
    crops = [
        ("s6_01_dharma_hall.jpg", "page_57_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_02_water_cup.jpg", "page_58_Im0.jpg", (0.1, 0.1, 0.9, 0.95)),
        ("s6_03_monk_teaching.jpg", "page_59_Im1.jpg", (0.0, 0.0, 0.85, 1.0)),
        ("s6_04_session_ends.jpg", "page_60_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_05_curious_students.jpg", "page_60_Im0.jpg", (0.2, 0.1, 0.9, 0.95)),
        ("s6_06_asking_monk.jpg", "page_61_Im1.jpg", (0.0, 0.0, 0.9, 1.0)),
        ("s6_07_monk_smiles.jpg", "page_61_Im1.jpg", (0.2, 0.1, 0.85, 0.95)),
        ("s6_08_too_much_water.jpg", "page_62_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_09_no_leftovers.jpg", "page_63_Im1.jpg", (0.0, 0.0, 0.85, 1.0)),
        ("s6_10_waste_not.jpg", "page_63_Im1.jpg", (0.2, 0.15, 0.95, 0.95)),
        ("s6_11_pouring_little.jpg", "page_64_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_12_finishing_water.jpg", "page_65_Im1.jpg", (0.0, 0.0, 0.9, 1.0)),
        ("s6_13_cherishing_effort.jpg", "page_66_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_14_water_is_life.jpg", "page_67_Im1.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_15_reverence_for_all.jpg", "page_68_Im0.jpg", (0.0, 0.0, 1.0, 1.0)),
        ("s6_16_gratitude_legacy.jpg", "page_68_Im0.jpg", (0.2, 0.1, 0.8, 0.95)),
    ]
    for out_name, in_name, box in crops:
        make_16x9_balanced(f"data/book_illustrations/{in_name}", f"data/book_illustrations/{out_name}", box)

    script_c6 = {
        "title": "Chương 6: Chuyện Ly Nước",
        "description": "Bài học thiêng liêng về đức tiết kiệm hiếu sinh và trân trọng từng giọt nước quý giá của Đức Trưởng lão Thích Thông Lạc.",
        "scenes": [
            {
                "scene_id": "scene_01",
                "text": "Mỗi thời pháp thoại của Thầy giảng dạy cho tu sinh và Phật tử tại Chơn Như thường kéo dài suốt nhiều tiếng đồng hồ.",
                "image_file": "data/book_illustrations/s6_01_dharma_hall.jpg"
            },
            {
                "scene_id": "scene_02",
                "text": "Trước giờ đăng giảng, các đệ tử luôn chu đáo rót sẵn một ly nước lọc trong trẻo đặt ngay ngắn trên bàn của Thầy.",
                "image_file": "data/book_illustrations/s6_02_water_cup.jpg"
            },
            {
                "scene_id": "scene_03",
                "text": "Trong suốt buổi giảng say sưa, dù nhiều người nghe cảm thấy khát, nhưng kỳ lạ thay Thầy không hề uống ngụm nước nào.",
                "image_file": "data/book_illustrations/s6_03_monk_teaching.jpg"
            },
            {
                "scene_id": "scene_04",
                "text": "Khi pháp hội kết thúc, mọi người cung kính xá chào Thầy lui ra, ly nước lọc trên bàn vẫn còn nguyên vẹn vẹn.",
                "image_file": "data/book_illustrations/s6_04_session_ends.jpg"
            },
            {
                "scene_id": "scene_05",
                "text": "Nhiều lần nhìn thấy ly nước vẫn y nguyên, lòng các đệ tử không khỏi băn khoăn trăn trở về nguyên do sâu xa phía sau.",
                "image_file": "data/book_illustrations/s6_05_curious_students.jpg"
            },
            {
                "scene_id": "scene_06",
                "text": "Một người học trò liền mạnh dạn tiến đến cung kính đảnh lễ và thưa hỏi: Bạch Thầy, sao Thầy không dùng ly nước?",
                "image_file": "data/book_illustrations/s6_06_asking_monk.jpg"
            },
            {
                "scene_id": "scene_07",
                "text": "Thầy mỉm cười đôn hậu, ánh mắt từ hòa nhìn người đệ tử rồi giãi bày tâm niệm sâu sắc của người tu giải thoát.",
                "image_file": "data/book_illustrations/s6_07_monk_smiles.jpg"
            },
            {
                "scene_id": "scene_08",
                "text": "Thầy bảo: Các con rót nhiều quá, Thầy uống rất ít nên không thể nào dùng hết được ly nước đầy như vậy.",
                "image_file": "data/book_illustrations/s6_08_too_much_water.jpg"
            },
            {
                "scene_id": "scene_09",
                "text": "Nếu Thầy uống dở dang thì nước sẽ còn thừa, mà người tu nên thừa tự chánh pháp chứ không thừa tự đồ thừa của người khác.",
                "image_file": "data/book_illustrations/s6_09_no_leftovers.jpg"
            },
            {
                "scene_id": "scene_10",
                "text": "Còn nếu đem đổ bỏ đi thì quá đỗi phí phạm giọt nước của đàn na tín thí, nên Thầy thà để nguyên vẹn không đụng tới.",
                "image_file": "data/book_illustrations/s6_10_waste_not.jpg"
            },
            {
                "scene_id": "scene_11",
                "text": "Thầy căn dặn các con từ nay chỉ cần rót một chút vừa đủ dùng, Thầy sẽ uống hết sạch không để lãng phí.",
                "image_file": "data/book_illustrations/s6_11_pouring_little.jpg"
            },
            {
                "scene_id": "scene_12",
                "text": "Hiểu được lời Thầy dạy, từ đó về sau các đệ tử chỉ rót lượng nước vừa đủ và Thầy luôn hoan hỷ uống cạn.",
                "image_file": "data/book_illustrations/s6_12_finishing_water.jpg"
            },
            {
                "scene_id": "scene_13",
                "text": "Có lần ly còn chút nước thừa, Thầy kiên nhẫn uống hết và nói: Mất công các con chắt chiu rót nước, Thầy phải uống trọn vẹn.",
                "image_file": "data/book_illustrations/s6_13_cherishing_effort.jpg"
            },
            {
                "scene_id": "scene_14",
                "text": "Nước chính là cội nguồn của sự sinh tồn trên địa cầu; biết tiết kiệm từng giọt nước là đang nâng niu mạng sống vạn loài.",
                "image_file": "data/book_illustrations/s6_14_water_is_life.jpg"
            },
            {
                "scene_id": "scene_15",
                "text": "Tình thương hiếu sinh đích thực không chỉ dành riêng cho con người và muôn thú, mà bao trùm cả cây cỏ, nguồn nước và tầng khí quyển.",
                "image_file": "data/book_illustrations/s6_15_reverence_for_all.jpg"
            },
            {
                "scene_id": "scene_16",
                "text": "Bài học về đức tiết kiệm hiếu sinh và lòng tri ân công sức của Thầy sẽ mãi khắc sâu trong tâm khảm của muôn đời Phật tử.",
                "image_file": "data/book_illustrations/s6_16_gratitude_legacy.jpg"
            }
        ]
    }
    with open("data/chapters/chapter6_script.json", "w", encoding="utf-8") as f:
        json.dump(script_c6, f, ensure_ascii=False, indent=2)
    print("Chapter 6 script saved!")

if __name__ == "__main__":
    generate_chapter_4()
    generate_chapter_5()
    generate_chapter_6()
    print("All chapters 4, 5, 6 prepared successfully!")
