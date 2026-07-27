def get_task_details(task_name: str):
    """
    Vazifa bo'yicha (maksimal_ball, kiritish_turi, standart_reja) ni qaytaradi.
    """
    # Har bir mezon uchun max ball va standart reja summasi belgilanadi
    tasks = {
        "📹 Har kuni ochilish videosi": (5, "media", 0),
        "🧹 Tozalik va tartib (10 ball)": (10, "media", 0),
        "📱 Instagram post": (5, "media", 0),
        "📸 Instagram stories": (5, "media", 0),
        "👀 3000+ ko'rish": (10, "media", 0),
        "💰 Savdo rejasi": (35, "amount", 1_500_000), # Masalan: Reja 1,500,000 so'm, max 35 ball
        "📉 Qarzdorlik oshmasligi": (-10, "amount", 1_000_000),
        "🎁 Bonus me'yoridan oshmasligi": (-10, "amount", 1_000_000)
    }
    return tasks.get(task_name, (0, "none", 0))

def calculate_proportional_score(task_name: str, amount: float) -> int:
    """
    Kiritilgan summani reja va maksimal ballga nisbatan proporsional hisoblaydi.
    Formula: (Kiritilgan summa * Maksimal ball) / Reja summasi
    """
    max_score, input_type, target_plan = get_task_details(task_name)
    
    if input_type != "amount" or target_plan <= 0:
        return max_score

    # Proporsional hisob-kitob (Proporsiya qoidasi)
    calculated = (amount * max_score) / target_plan
    
    # Agar minus ball bo'lsa (masalan, qarzdorlik)
    if max_score < 0:
        return int(calculated) if calculated < 0 else 0
        
    return int(calculated)