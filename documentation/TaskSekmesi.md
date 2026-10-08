Task sekmesinden ayarlanabilir bir hedef eklemesi koyacağız. Bu hedef planlanan pomodoroları tutacak falan filan.

aklımdak ifikir şu:
yeni bir @dataclass oluşturacağız, bu hedef tutmak amacıyla yapılacak. içerisine eklenen "Task"leri alacak ve onlar üzerinden itere ederek hedefin gerekle hesaplamalarını falan halledecek. Örneğin:
Kendimize çalışmak amacıyla 3 pomodoro 'İşaretler ve Sistemler' görevi vereceğiz. Bu o görev için atadığımız 3 tanesini bu yeni yaptığımız görev/ödev classına ekleyecek, toplam sürelerini hesaplayacak, gibi gibi. Bu sayede istediğimizi sıradan çıkartıp araya ekleme yapabilir, tekil tasklerde oynamalara gidebilir manipüle edebiliriz.

