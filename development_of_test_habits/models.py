from django.db import models


class School(models.Model):
    name = models.CharField(max_length=32)


class Class(models.Model):
    school_id = models.ForeignKey(to=School, on_delete=models.PROTECT)
    name = models.CharField(max_length=32)


class Student(models.Model):
    class_id = models.ForeignKey(to=Class, on_delete=models.PROTECT)
    name = models.CharField(max_length=32)


class HomeWork(models.Model):
    student_id = models.ForeignKey(to=Student, on_delete=Student)
    name = models.CharField(max_length=32)


