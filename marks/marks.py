import csv
top = []
subj = []
total = []
names = []
subjs = ['Maths','Biology','English','Physics','Chemistry','Hindi']
for m in range(6):
    top.append(0)
    subj.append(0)
i = 0
with open('Student_marks_list.csv','r') as file:
    csv_file = csv.reader(file)
    next(csv_file)
    for row in csv_file:
        names.append(row[0])
        for j in range(6):
            k = 0
            if(int(top[j])<int(row[j+1])):
                top[j]=row[j+1]
                subj[j]=row[0]
        total.append(int(row[1])+int(row[2])+int(row[3])+int(row[4])+int(row[5])+int(row[6]))
        i+=1
new_list = sorted(total,reverse=True)
for j in range(6):
    print('Topper in {} is {}'.format(subjs[j], subj[j]))
print("---------------------------------")
print("Best Students in the class are : ")
for j in range(3):
    x = total.index(new_list[j])
    print('{} : {}'.format(j+1,names[x]))

#The time complexity for this program is O(6n) => O(n) for finding the toppers
#in each subject and O(3n) => O(n) for finding the best 3 students in the class.
