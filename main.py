import argparse
import os
import random

import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
from datacenter.models import (
    Schoolkid, Mark, Lesson, Commendation, Chastisement, Subject
)


commendations = [
    'Молодец!', 'Отлично!', 'Хорошо!', 'Гораздо лучше, чем я ожидал!', 'Ты меня приятно удивил!',
    'Великолепно!', 'Прекрасно!', 'Ты меня очень обрадовал!', 'Именно этого я давно ждал от тебя!',
    'Сказано здорово – просто и ясно!', 'Ты, как всегда, точен!', 'Очень хороший ответ!', 'Талантливо!',
    'Ты сегодня прыгнул выше головы!', 'Я поражен!', 'Уже существенно лучше!', 'Потрясающе!',
    'Замечательно!', 'Прекрасное начало!', 'Так держать!', 'Ты на верном пути!', 'Здорово!',
    'Это как раз то, что нужно!', 'Я тобой горжусь!', 'С каждым разом у тебя получается всё лучше!',
    'Мы с тобой не зря поработали!', 'Я вижу, как ты стараешься!', 'Ты растешь над собой!',
    'Ты многое сделал, я это вижу!', 'Теперь у тебя точно все получится!'
    ]


def fix_marks(schoolkid):
    '''исправляет все оценки ниже 4 на 5'''
    marks = Mark.objects.filter(schoolkid=schoolkid, points__lt=4).all()
    if not marks: return 0
    for mark in marks:
        mark.points = 5
        mark.save()
    return marks.count()


def remove_chastisements(schoolkid):
    '''удаляет все замечания ученика'''
    chastisements = Chastisement.objects.filter(schoolkid=schoolkid).all()
    return chastisements.delete()[0]


def create_commendation(schoolkid, subject, text):
    lesson = Lesson.objects.filter(
        year_of_study=schoolkid.year_of_study,
        group_letter=schoolkid.group_letter,
        subject=subject
        ).order_by('?').first()
    commendation = Commendation.objects.create(
        text=text,
        created=lesson.date,
        schoolkid=schoolkid,
        subject=lesson.subject,
        teacher=lesson.teacher
        )
    return commendation


def main():
    parser = argparse.ArgumentParser(description="Исправим карму в дневнике")
    parser.add_argument('surname', help='Имя ученика')
    parser.add_argument('subject', help='Предмет')
    args = parser.parse_args()
    surname = args.surname
    subject = args.subject
    year_of_study = 6
    group_letter = 'А'
    try:
        schoolkid = Schoolkid.objects.get(
            full_name__contains=surname,
            year_of_study=year_of_study,
            group_letter=group_letter)
        print(f'Исправлено оценок - {fix_marks(schoolkid)}')
        print(f'Удалено замечаний - {remove_chastisements(schoolkid)}')
        subject = Subject.objects.get(title=subject, year_of_study=year_of_study)
        commmendation = create_commendation(schoolkid, subject, random.choice(commendations))
        print(
            f'Лайк "{commmendation.text}" от'
            f' {commmendation.teacher} по'
            f' {commmendation.subject}'
            )
    except Schoolkid.DoesNotExist:
        print(f'Не нашёл ученика "{surname}" в классе "{year_of_study}{group_letter}"')
    except Schoolkid.MultipleObjectsReturned:
        print(f'Несколько учеников "{surname}" в классе "{year_of_study}{group_letter}"')
    except Subject.DoesNotExist:
        print(f'Предмет  "{subject}" в классе "{year_of_study}" не найден')


if __name__ == '__main__':
    main()
