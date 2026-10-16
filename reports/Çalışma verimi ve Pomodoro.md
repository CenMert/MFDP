# Zamanlayıcıyı değil, ölçümü ve tekrarı optimize edin

Araştırmanın ana bulgusu şu: **25/5 Pomodoro zamanlayıcısı tek başına daha fazla iş çıkarmayı sağlamıyor. Asıl kazanç, molaları dışarıdan belirlemenin getirdiği daha iyi ruh hali ve daha az yorgunlukta, Cirillo'nun asıl yönteminin özü olan ölçme-tahmin-gözden geçirme döngüsünde ve neyin nasıl çalışıldığında** (aralıklı tekrar, kendini test etme). Pomodoro'yu doğrudan test eden az sayıdaki kontrollü çalışma (hepsi üniversite öğrencileriyle ve tek oturumluk) iki şey gösteriyor. Sabit molalar, molayı kendi belirleyen öğrencilere göre daha az yorgunluk ve daha yüksek konsantrasyon sağladı ama görev tamamlama aynı kaldı. 2025'teki takip çalışması ise Pomodoro'da yorgunluğun oturum içinde daha hızlı arttığını buldu. Davranış değişikliği literatürünün en sağlam bulguları da MFDP için önemli. Hedefe göre ilerlemeyi izlemek hedefe ulaşmayı d ≈ 0,40 artırıyor. "Eğer-ise" planları d ≈ 0,65 etki gösteriyor. Alışkanlığın otomatikleşmesi medyan 66 gün sürüyor ve tek bir günü kaçırmak süreci bozmuyor. Kırılan "streak"ler ise motivasyonu düşürüyor. MFDP'nin mevcut veri modeli (`sessions_v2` + `atomic_events` + `tasks` + takvim) şema değiştirmeden yaklaşık 15 araştırmayla uyumlu metrik üretebilir: kişisel en verimli saatler, ilk kesintiye kadar geçen süre, tahmin-gerçek oranı, gün içi yorgunluk eğrisi, sınav öncesi "son dakika" eğrisi gibi. En değerli eksik veriler ise oturum sonu 1–5 odak puanı ve kesintinin iç/dış ayrımı. Bu rapor bu verilerin nasıl kullanılacağını, uygulamanın kullanıcıyı nasıl daha disiplinli yapabileceğini, Pomodoro'nun nasıl yanlış kullanıldığını ve hangi çalışma yöntemlerinin gerçekten kanıta dayandığını, güçlü kanıtı popüler iddiadan ayırarak ele alıyor.

> **Okuma notu:** Kanıt düzeyleri metin boyunca şöyle işaretlendi: **[Güçlü]** = birden fazla meta-analiz veya geniş, tutarlı deneysel literatür; **[Orta]** = birkaç deney veya moderatörlü/karışık sonuçlu meta-analiz; **[Zayıf/Popüler]** = kitap, blog, firma verisi, gözlemsel ya da tek küçük çalışma; **[Doğrulanmadı]** = araştırmacıların birincil kaynakta teyit edemediği iddia. MFDP'ye dair öneriler araştırmacıların ve bu raporun **çıkarımlarıdır**. Hiçbiri doğrudan test edilmiş bir protokol değildir.

---

## 1. MFDP'nin verisi bugün 15'e yakın araştırma metriği üretebilir

### Literatürün odak ve verimlilikle ilişkilendirdiği dört sinyal

İnsan-bilgisayar etkileşimi (HCI) ve psikoloji literatüründe odak ve verimlilikle en çok ilişkilendirilen davranış sinyalleri dörde ayrılıyor. Birincisi **dikkatin parçalanması**, yani bir ekranda ya da görevde ne kadar kalındığı. İkincisi **kesintiler**, kendiliğinden (iç) ve dışarıdan gelen olarak ikiye ayrılıyor. Üçüncüsü **günün saati ve haftanın günü**, dördüncüsü **molalar**. Gloria Mark'ın ekibinin ölçümlerine göre bilgi çalışanlarının bir ekranda kesintisiz kalma süresi 2004'te ~2,5 dakikaydı, 2012'de ~75 saniyeye ve 2016 sonrasında ortalama ~47 saniyeye (medyan ~40 s) düştü. Mark bu sayının biyolojik bir dikkat sınırı değil, *ekran değiştirme* ölçüsü olduğunu ve her geçişin dikkat dağınıklığı sayılmayacağını özellikle vurguluyor ([Steelcase röportajı](https://www.steelcase.com/research/articles/our-47-second-attention-span-with-gloria-mark-s5-ep3-transcript/)). "Neurotics Can't Focus" çalışmasında 40 çalışan iki hafta boyunca izlendi ve **kısa odak süreleri gün sonundaki daha düşük öz-değerlendirmeli verimlilikle ilişkili çıktı** ([Mark ve ark., CHI 2016](https://www.microsoft.com/en-us/research/?p=238240)). Bu bulgu, bir oturum sonu öznel puanının anlamlı bir "etiket" olabileceğini gösteriyor. 32 çalışanla yapılan "Bored Mondays and Focused Afternoons" çalışmasında öznel odak **öğleden sonranın ortasında zirve yaptı** ([Mark ve ark., CHI 2014](https://isr.uci.edu/node/2035.html)). Bu çalışmaların hepsi küçük örneklemli (n ≈ 14–90), korelasyonel ve kişi-içi örüntüler gösteriyor [Orta].

### Kesintiler: çıktı düşmüyor, stres artıyor

Kesintiler konusunda iki sonuç MFDP'nin tasarımını doğrudan etkiliyor. Laboratuvarda kesintiye uğrayan katılımcılar e-posta görevlerini **daha hızlı ve kalite kaybı olmadan** bitirdi, ama anlamlı ölçüde **daha fazla stres, hayal kırıklığı, zaman baskısı ve çaba** bildirdi ([Mark, Gudith & Klocke, CHI 2008](https://www.interruptions.net/literature/Mark-CHI08.pdf)) [Orta]. Bu yüzden MFDP'nin "tamamlandı" verisi kesintinin bedelini görmeyebilir. Bedel çıktıda değil, deneyimde. 36 kişinin 889 saatlik gözlemlenen görev geçişlerini analiz eden çalışma ise kendi kendini kesmenin, kişinin **yakın zamanda yaşadığı dış kesintilerle arttığını** gösterdi ([Dabbish, Mark & González, CHI 2011](https://isr.uci.edu/node/1353.html)). İç ve dış kesinti birbirini besliyor. Bugün MFDP'de her duraklatma `interruption_detected{reason: "user_pause"}` olarak kaydediliyor ve bu iki tür birbirinden ayrılmıyor.

### MFDP'nin bugün kaydettikleri ve kaydetmedikleri

Veri haritasına göre MFDP şu sinyalleri **zaten kaydediyor**:

- Zaman bilgisi: `sessions_v2.start_time`/`end_time`, yerel saat.
- Net süre: `duration_seconds`, duraklatmalar hariç.
- Plan ve mod: `planned_duration_minutes` ve `mode`.
- Sonuç: `completed`.
- Görev ve etiket: `task_name` ve `category`.
- Her duraklatma: `interruption_detected`. Metadata'sında `active_seconds` ve `interruption_number` var.
- Her devam ediş: `session_resumed`. Metadata'sında `pause_seconds` ve `active_seconds` var.
- İlerleme: %25/50/75 eşikleri için `milestone_reached`, yalnızca Focus modunda.
- Bitiş: `session_completed` (`focus_completion_ratio`) ve `session_abandoned` (`reason`: `reset`/`mode_change`/`app_exit`).
- DND değişiklikleri: `dnd_toggled`.

Kaydedilmeyenler de belli. Pencere değişimi (`focus_shift_detected`) tanımlı ama `SystemMonitor` hiçbir yerde oluşturulmuyor. `break_started`/`break_ended`, `distraction_identified` ve `environment_changed` da hiçbir yerden çağrılmıyor. Takvim tabloları oturum verisine bağlı değil. Kısacası MFDP **oturumun ne zaman ve ne kadar sürdüğünü iyi biliyor, oturum *sırasında* ne olduğunu ise kör ölçüyor**. Mark tarzı araştırmalara göre ana boşluk bu.

### Hesaplanabilir metrikler ve şemaya özgü tuzaklar

Aşağıdaki tablo, ek veri toplamadan hesaplanabilecek metrikleri ve dayandıkları araştırmayı özetliyor. Sorgu tasarımları araştırmacının önerisi. Veri haritasına göre üç düzeltme gerekiyor:

1. `sessions_v2.interruption_count` yalnızca duraklatmaları değil, **kapanış nedenlerini de** (reset/mod değişimi/app_exit) sayıyor. Saf kesinti oranı için `interruption_detected` olaylarını saymak gerekiyor.
2. `atomic_events.elapsed_seconds` duvar saati süresi. Net süre için `json_extract(metadata,'$.active_seconds')` kullanılmalı.
3. `stats_window` takvim gününü (00:00), gün paneli ise 03:00'te başlayan mantıksal günü kullanıyor. Analizlerde tek bir gün tanımı seçilmeli.

| Metrik | Kaynak alanlar | Neyi gösterir / dayanağı |
|---|---|---|
| Saat × gün "kronotip profili" (odak dakikası, tamamlanma oranı) | `sessions_v2.start_time`, `completed`, `mode` | Kişisel en verimli saatler. Mark 2014'teki öğleden sonra zirvesi ve kronotip uyumu literatürüyle karşılaştırılabilir. Hücre başına n ≥ 5 bir sezgisel eşik, kanıtlanmış bir alt sınır değil |
| Terk nedenine göre tamamlanma | `session_abandoned.reason` | `mode_change`/`app_exit` başarısızlık sayılmamalı. Yalnızca `reset` gerçek bir vazgeçme sinyali |
| Odak saati başına kesinti | `interruption_detected` sayısı / net süre | Haftalık trend, etiket ve saat kırılımı |
| İlk kesintiye kadar geçen süre (sağkalım analizi) | İlk `interruption_detected` olayının `active_seconds`'ı. Kesintisiz oturumlar süresinde "sansürlü" sayılır | Kaplan–Meier medyanı kişisel bir "odak süresi" verir. Mark'ın 40–47 saniyesinin Pomodoro ölçeğindeki karşılığı |
| Duraklatma süresi dağılımı | `session_resumed.pause_seconds` | Medyan ve P90. 10 dakikayı aşan duraklamalar büyük olasılıkla dış kesinti ya da bağlam kaybı. Toplam duraklama / (aktif + duraklama) = parçalanma oranı |
| Kilometre taşı kayıp eğrisi | `milestone_reached.percentage` | Oturumların *nerede* öldüğü: %25'te mi, %75'te mi? |
| Tahmin doğruluğu | `duration_seconds` / `planned_duration_minutes`; görev düzeyinde toplam süre / `tasks.planned_duration_minutes` | Planlama yanılgısı. Medyan oranın 1'den büyük çıkması beklenir |
| Mola uyumu | Focus oturumundan sonra N dakika içinde gelen Short/Long Break satırı ve bu molanın gerçek/planlanan uzunluğu | Biwer 2023'ün kişisel testi: mola yapılınca sonraki oturum daha iyi gidiyor mu? |
| Gün içi yorgunluk | Günün kaçıncı oturumu olduğu (`ROW_NUMBER() OVER (PARTITION BY gün)`) ile tamamlanma ve kesinti oranı | Eğim düşüyorsa kişisel bir "günlük tavan" eşiği |
| Tutarlılık | En az X dakika odaklanılan gün sayısı; günlük dakikanın değişim katsayısı | Alışkanlık metriği (bkz. Bölüm 3) |
| Derin bloklar | Aynı görev için arada ≤ 30 dk olan oturum blokları (`BLOCK_GAP_MINUTES`) | Kesintisiz uğraş ve günlük görev geçişi sayısı |
| Sınav öncesi "son dakika" eğrisi | `calendar_events` (`kind IN ('sinav','odev')`) için −21…0. günlerdeki odak dakikaları | Hazırlığın son 3 güne düşen payı. Yalnızca betimsel |
| En iyi oturum uzunluğu | `planned_duration_minutes` × P(tamamlanma), Beta(1,1) aralıklarıyla | Ham tamamlanma oranı yerine **beklenen tamamlanmış odak dakikası** |
| DND etkisi | `dnd_toggled` açık/kapalı oturumlarda kesinti oranı | Gözlemsel. Niyet karıştırıcı bir değişken |
| Rejim değişikliği | Haftalık odak dakikası üzerinde change-point (ör. `ruptures`) | Dönem başı, sınav haftası, yeni alışkanlık |

### Tek kullanıcılı veride doğru istatistik

Tek kullanıcılı ve birkaç yüz ile birkaç bin oturum arasındaki bir veride karmaşık makine öğrenmesi yerine şu araçlar daha uygun: medyan ve çeyrekler açıklığıyla betimsel istatistik, sağkalım analizi (Python'da `lifelines`), 3–5 değişkenli lojistik regresyon, seyrek hücreler için Bayesçi beta-binom güncellemesi ve change-point tespiti. Model değerlendirmesinde rastgele bölme değil, zaman sıralı çapraz doğrulama kullanılmalı. Bu yöntem seçimleri araştırmacının çıkarımı ve doğrudan bir kaynağa dayanmıyor.

### Eklenmeye değer veriler, değer/maliyet sırasıyla

Önerilerin dayanağı şöyle. Mark 2016, öz-değerlendirmeli verimliliğin odak süresiyle ilişkili olduğunu gösterdi. Meyer ve arkadaşlarının 43 geliştiricili saha çalışmasında periyodik öz-bildirim (experience sampling) farkındalığı artırdı ([Meyer ve ark., CSCW 2018](https://www.merlin.uzh.ch/publication/show/15499)). İç/dış ayrımı ise Cirillo'nun kanonik kayıt biçimi ([U. Waterloo özeti](https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf)). Bu gerekçelerle en değerli üç ekleme şunlar:

1. **Oturum sonu 1–5 odak (isteğe bağlı enerji/ruh hali) puanı.** Maliyeti oturum başına tek tık. Metrikleri niceliğin yanında *nitelikle* de etiketler ve denetimli bir modele zemin hazırlar.
2. **Duraklatmada iç/dış kesinti seçimi.** Maliyeti duraklatma başına tek tık. İsteğe bağlı olarak telefon, kişi, açlık, yorgunluk gibi kategoriler eklenebilir. Bu ayrım hedefli öneriyi mümkün kılar: dış kesintiye DND, iç kesintiye görevi parçalamak.
3. **`focus_shift_detected`'in bağlanması.** Yalnızca uygulama sınıfı, yerel ve opt-in olmalı. Pencere başlıkları hassas veri olduğu için kaydedilmemeli ya da hash'lenmeli. Böylece Mark tarzı ekran-odak süresi ve "en çok bölen uygulama" (Rize benzeri) metrikleri elde edilir.

Bunları şu eklemeler izliyor:

- Görev zorluğu ya da türü (yeni konu/tekrar/pratik).
- Sınav notu gibi bir sonuç ölçüsü. Süreç metriklerinin gerçekten işe yarayıp yaramadığını test etmenin tek yolu bu.
- Günlük uyku girişi.
- Mola aktivitesi etiketi (ekran/yürüyüş/telefon). `break_started`/`break_ended` API'si zaten var.
- Kişisel deneyler için bir `experiment_id` alanı.

Öz-bildirim istemlerinin aylar içinde yorgunluk veya yanlılık yaratıp yaratmadığına dair kaynak bulunamadı. Bu yüzden istemler kısa ve isteğe bağlı tutulmalı.

---

## 2. Bu veri en çok tahmin, zamanlama ve kişisel deneyde işe yarar

### Planlama yanılgısının düzeltilmesi

MFDP'nin veri toplama biçimi en güçlü şekilde **planlama yanılgısında** işe yarıyor. Buehler, Griffin ve Ross'un klasik çalışmasında 37 öğrenci tezlerini ortalama 33,9 günde bitireceğini tahmin etti. Gerçekte bu süre 55,5 gün oldu ve yalnızca ~%30'u tahmin ettiği tarihte bitirdi. İnsanlar başkalarının işini değil, **kendi işlerini** iyimser tahmin ediyor. Katılımcılara tahmini geçmiş deneyimleriyle ilişkilendirmeleri söylendiğinde yanlılık ortadan kalktı ([Buehler ve ark., 1994](https://bear.warrington.ufl.edu/brenner/mar7588/Papers/buehler-et-al-1994.pdf)) [Orta; tez sayıları ikincil kaynaklardan]. Bu bulgu doğrudan bir özelliğe çevrilebilir. Kullanıcı bir göreve süre girerken, aynı etiket veya üst görev altındaki benzer geçmiş görevlerin gerçek sürelerini görmeli. Uygulama da kişisel bir **kalibrasyon katsayısı** önerebilir: "tahminlerin tipik olarak 1,6× düşük; önerilen 8 pomodoro". `tasks.planned_duration_minutes` şu an "bilgi amaçlı" duruyor ve bu özellik için hazır bir kanca.

### Zamanlama: günün saati, uyku ve sınav takvimi

İkinci kullanım alanı **zamanlama**. Kronotip uyumu (kişinin tercih ettiği saatte daha iyi performans) genç yetişkinlerde tutarsız. 65 çalışmalık bir sistematik derlemede çalışmaların %80'inden fazlası kronotipin bilişe ana etkisini bulmadı. Uyum etkisi 18–45 yaş arasındaki çalışmaların yalnızca 29/64'ünde (%45) görüldü, yaşlı yetişkinlerde ise 10/12'sinde ([Chauhan ve ark., 2025](https://researchinnovation.kingston.ac.uk/en/publications/chronotype-and-synchrony-effects-in-human-cognitive-performance-a/)) [Orta]. Bu yüzden genel "sabah insanı/akşam insanı" kuralları yerine **kişinin kendi verisinden çıkarılan saat profili** daha savunulabilir. MFDP bunu saat bazında tamamlanma ve kesinti oranından hesaplayabilir.

Uyku konusunda daha net bir bulgu var. MIT'de 88 öğrencinin Fitbit verisinde uykunun kalitesi, süresi ve düzenliliği birlikte not varyansının **~%24'ünü** açıkladı. Sınavdan *önceki tek gecenin* uykusu ise notu öngörmedi. Önceki hafta ve ayın uykusu öngördü ([Okano ve ark., 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6773696)) [Orta; korelasyonel, tek ders]. MFDP bunu sınav haftasında gece geç saatte (ör. 01:00–02:00 sonrası) başlayan oturumları sayan ve uyaran bir özelliğe çevirebilir.

Takvimdeki `sinav` kayıtları da **aralıklı tekrar** zamanlamasını mümkün kılıyor. 1.350'den fazla katılımcıyla yapılan çalışmada en iyi tekrar aralığı, sınava kalan sürenin 1 haftalık ufukta **~%20–40'ı**, 1 yıllık ufukta **~%5–10'u** çıktı. Çok kısa aralık, çok uzun aralıktan daha zararlı ([Cepeda ve ark., 2008](https://pubmed.ncbi.nlm.nih.gov/19076480/)) [Güçlü]. Bunun pratik karşılığı kabaca şöyle:

| Sınava kalan süre | Önerilen tekrar aralığı |
|---|---|
| 1 hafta | 1–2 gün |
| 1 ay | ~1 hafta |
| Dönem sonu (~3 ay) | 1–2 hafta |

### Gün içi yorgunluk ve günlük odak bütçesi

Üçüncü kullanım alanı **yorgunluk ve günlük kapasite**. Popüler "günde ~4 saat derin çalışma" sınırı Newport'un *Deep Work* kitabında Ericsson'a dayandırılıyor. Ericsson'ın keman öğrencileri üzerine 1993 makalesinde ise araştırmacılar böyle sert bir tavana dair doğrudan bir ifade bulamadı ([Unhustle analizi](https://unhustle.substack.com/p/the-10000-hour-rule-myth-and-the)) [Zayıf/Popüler]. Daha yeni bir nörometabolik çalışma, yaklaşık bir iş günü boyunca yoğun bilişsel kontrol gerektiren görevlerden sonra lateral prefrontal kortekste glutamatın arttığını ve seçimlerin düşük çabalı, kısa vadeli seçeneklere kaydığını gösterdi ([Wiehler ve ark., 2022](https://hal.sorbonne-universite.fr/hal-04534917)) [Orta; N ≈ 40, tek çalışma, nedensellik teyit edilmedi]. MFDP için dürüst yaklaşım sabit bir "4 saat" kuralı değil. Kullanıcının günün k'ıncı oturumunda tamamlanma ve kesinti oranının nasıl değiştiğini gösteren **kişisel yorgunluk eğrisi** daha uygun. 3–4 saat ise yalnızca yumuşak bir uyarı eşiği olarak sunulabilir.

### Kişisel (N-of-1) deneyler

Dördüncü ve belki en ilginç kullanım alanı **kişisel deney**. Bölüm 4'te anlatılacağı gibi iki Hollanda çalışması sabit ve esnek mola konusunda farklı sonuçlara vardı. Bu çelişki, kullanıcının kendi üzerinde ABAB düzeninde ya da günlük rastgele atamayla 25 ve 50 dakikalık oturumları veya sabit ve serbest molayı karşılaştırması için iyi bir gerekçe. IBS hastalarıyla yapılan TummyTrials çalışması, yapılandırılmış kişisel deneylerin uygulanabilir olduğunu gösterdi. Aynı çalışma, bilimsel geçerlilik ile protokole uymanın günlük deneyimi arasında bir **gerilim** olduğunu ve katılımcıların esneklik istediğini de buldu ([Karkar ve ark., CHI 2017](https://pmc.ncbi.nlm.nih.gov/articles/PMC5432136)) [Orta].

### Analizde kaçınılması gereken tuzaklar

- **Goodhart yasası.** Tamamlanma oranı hedef olursa kullanıcı kısa oturum planlar ya da zor görevlerden kaçar. Bu yüzden tamamlanma oranı her zaman planlanan dakikayla birlikte gösterilmeli. Bu ilke kavramsal bir risk; kişisel takip uygulamalarına özgü ampirik bir çalışma bulunamadı.
- **Karıştırıcı değişkenler.** Örneğin sınav yakınlığı hem çalışma saatini hem görev seçimini etkiler.
- **Veri boşlukları.** Epstein ve arkadaşlarının modeline göre takibe ara vermek normaldir ([Epstein ve ark., UbiComp 2015](https://my.eng.utah.edu/~cs5540/au16/readings/PersonalInformatics-Epstein2015.pdf)). Boş günler "sıfır verim" sayılmamalı.
- **Son tarih öz-yaptırımları.** Ariely ve Wertenbroch'un 2002'de bulduğu "kendi koyduğun son tarih erteleme davranışını azaltır" etkisi, 2026'daki bir replikasyonda ihmal edilebilir çıktı ([Hyndman & Bisin, 2026](https://journals.sagepub.com/doi/full/10.1177/09567976261460772)). Bu nedenle son-dakika eğrisi yalnızca **betimsel** bir araç olarak sunulmalı.

---

## 3. Disiplin iradeden değil, bağlamdan, plandan ve hoşgörülü izlemeden doğar

### İrade bir pil değil

Disiplinli olmanın en sık yanlış anlaşılan yanı "irade"nin harcanan bir kaynak olduğu fikri. Ego tükenmesi etkisinin 23 laboratuvarda ve 2.141 katılımcıyla yapılan ön-kayıtlı replikasyonu **d = 0,04** buldu (%95 GA [−0,07; 0,15]). Orijinal etki d = 0,69'du ([Hagger ve ark., 2016](https://kops.uni-konstanz.de/entities/publication/b014f185-b8d7-4fb7-85de-173bc46581f1)) [Güçlü; replikasyon]. Baumeister ve Vohs manipülasyona itiraz etti ve bazı yorumcular kanıtın etkiyi ne kanıtladığını ne de çürüttüğünü söylüyor. Yine de MFDP'de bir "irade metresi" ya da "iradeni sakla" mesajı kurmak için sağlam bir zemin yok.

Daha sağlam bulgu şu: öz-denetimi yüksek insanlar ayartmaya daha çok direnen insanlar değil, **daha güçlü yararlı alışkanlıkları olan** insanlar. 2.274 kişilik altı çalışmada alışkanlıklar, öz-denetim ile ödev tamamlama, not ortalaması ve üniversitede kalıcılık arasındaki ilişkiye aracılık etti ([Galla & Duckworth, 2015](https://pmc.ncbi.nlm.nih.gov/articles/PMC4731333)) [Orta; korelasyonel/boylamsal]. Aynı makalenin aktardığı bir meta-analize göre özellik olarak öz-denetim, *otomatik* istenen davranışları (r = 0,36) *kontrollü* olanlardan (r = 0,15) daha güçlü öngörüyor ([de Ridder ve ark. 2012, Galla & Duckworth üzerinden](https://pmc.ncbi.nlm.nih.gov/articles/PMC4731333)). Pratik sonucu: **çevreyi kolaylaştırmak, ayartmayla savaşmaktan daha etkili.** MFDP'de bu, oturum başında otomatik DND ve isteğe bağlı olarak dikkat dağıtıcı uygulama tespiti anlamına geliyor.

### Alışkanlık: 21 değil, medyan 66 gün; tek kaçırma zararsız

"21 günde alışkanlık" bir halk inanışı. 96 gönüllünün 84 gün boyunca otomatiklik bildirdiği saha çalışmasında, modelin plato noktasının %95'ine ulaşma süresinin medyanı **66 gün**, aralığı ise **18–254 gün** çıktı. Bu değer yalnızca modele iyi uyan katılımcılardan hesaplandı. Kritik bulgu şu: **"Davranışı bir kez yapmamak alışkanlık oluşumunu kayda değer biçimde etkilemedi."** Çok tutarsız katılımcılarda ise alışkanlık oluşmadı ([UCL haber özeti](https://www.ucl.ac.uk/news/2009/aug/how-long-does-it-take-form-habit); [Behavioral Scientist](https://www.thebehavioralscientist.com/articles/how-long-to-form-a-habit)) [Zayıf–Orta]. Bu kanıtın sınırları var: modele uyan alt örneklem yalnızca 39 kişiydi, çalışma henüz replike edilmedi ve otomatiklik tamamen öz-bildirime dayanıyor ([PCI RR ön-baskısı](https://rr.peercommunityin.org/download/t_recommendations.reply_pdf.8382af6b73bdd0f7.6d616e757363726970745f7072657072696e742e706466.pdf)). Ayrıca derin çalışma, "öğlen su içmek"ten çok daha karmaşık bir davranış. 66 gün bu yüzden muhtemelen bir alt sınır.

Teorik çerçeveye göre alışkanlık, aynı bağlamda (aynı saat, yer ya da önceki eylem) tekrarlanan davranışın bağlamla kurduğu ilişkiden doğuyor. Oluştuktan sonra bağlamı algılamak davranışı hedefe ihtiyaç duymadan tetikliyor ([Wood & Neal, 2007](https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf)). Buradan iki MFDP fikri çıkıyor. Birincisi, ana alışkanlık metriği ham dakika değil **başlama saati ve yerinin tutarlılığı** olmalı ("oturumlarının %80'i 09:00–09:30 arasında başladı"). İkincisi, katı günlük streak yerine **"son 7 günün 5'i"** veya **"iki kez üst üste kaçırma"** gibi kaçırmaya hoşgörülü bir tutarlılık ölçüsü kullanılmalı.

### Eğer-ise planları: en iyi etki/maliyet oranı

Davranış değişikliği literatüründe uygulama maliyetine göre en güçlü araç **uygulama niyetleri**, yani eğer-ise planları. Örnek bir plan: "Saat 09:00'da masama oturduğumda, 3. bölüm için 25 dakikalık bir pomodoro başlatırım." 94 bağımsız testin meta-analizinde hedefe ulaşma üzerindeki etki **d = 0,65** çıktı ve yazarlar bunu "orta-büyük" olarak nitelendirdi ([Gollwitzer & Sheeran, 2006](https://kops.uni-konstanz.de/entities/publication/2e749bfb-8533-437c-8203-7e788c910c5f); [Frontiers 2021, %95 GA 0,6–0,7](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.565202/full)) [Güçlü]. Bu çalışmaların çoğu sağlık davranışları üzerine. Ders çalışma verimine özgü çalışma az.

Zihinsel karşıtlama ile birleştirilmiş hali (MCII/WOOP: Dilek, Sonuç, Engel, Plan) daha küçük ama anlamlı bir etki gösteriyor: 21 çalışma ve 15.907 katılımcıda **g = 0,336**. Etki deneyciyle etkileşimde g = 0,465, kendi kendine yürütülen formatta ise g = 0,277. Yazarlar yayın yanlılığı nedeniyle gerçek etkinin daha küçük olabileceğini belirtiyor ([Wang, Wang & Gai, 2021](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8149892/)) [Orta]. Sağlık davranışlarına yönelik ayrı bir meta-analizde zihinsel karşıtlamaya eğer-ise planı eklemek etkiyi anlamlı biçimde artırmadı ([Cross & Sheffield, 2019](https://pubmed.ncbi.nlm.nih.gov/30879403/)).

MFDP için öneriler:

- Görev planlarken bir "ne zaman/nerede → ilk somut eylem + pomodoro sayısı" alanı.
- "YouTube'u açma isteği gelirse, onu dikkat listesine yazar ve devam ederim" türünden bir engel planı. Bu plan duraklatma kaydına bağlanabilir.
- Hafta başında dört kısa alandan oluşan, form yerine yönlendirmeli bir diyalog şeklinde etkileşimli bir WOOP sihirbazı.

### İzleme işe yarar, ama bir hedefe göre ve kaydederek

138 RKÇ ve 19.951 katılımcılık meta-analiz, ilerlemeyi izleme sıklığını artıran müdahalelerin hedefe ulaşmayı **d = 0,40** artırdığını gösterdi. Etki, bilgi **fiziksel olarak kaydedildiğinde** ve **başkalarına bildirildiğinde ya da kamuya açıldığında** daha büyüktü ([Harkin ve ark., 2016](https://eprints.whiterose.ac.uk/id/eprint/91437/)) [Güçlü; çoğunlukla sağlık hedefleri]. Hedef teorisi de aynı yönü gösteriyor. Belirsiz "elinden geleni yap" hedefleri yerine **spesifik ve zorlayıcı hedefler** dikkati yönlendiriyor, çabayı ve ısrarı artırıyor ve strateji keşfini destekliyor. Bunun için hedefe bağlılık, geri bildirim ve yeterli yetenek gerekiyor. Karmaşık işlerde öğrenme hedefleri ve yakın ara hedefler daha uygun ([Locke & Latham, 2002](https://home.ubalt.edu/tmitch/642/articles%20syllabus/locke%20pract%20goal%20setting%202002%20am%20psy.pdf)) [Güçlü; geniş literatürün anlatısal derlemesi]. Bu yüzden MFDP'de takip edilen süre her zaman **bir hedefe göre** gösterilmeli ("bu hafta Tez 3. bölüm: 6 pomodoronun 4'ü"). Bir sonraki haftanın hedefi keyfi değil, son haftaların medyanı +%10 gibi kalibre edilmiş bir değer olmalı. Özyinelemeli görev ağacı, uzak hedefleri haftalık ve günlük ara hedeflere bölmeye zaten uygun.

### Ölçmenin bedeli ve takibi bırakmanın doğallığı

Ölçmenin bir bedeli de var. Altı deneyde bir etkinliği ölçmek etkinliğin miktarını artırdı, ama **ondan alınan keyfi azalttı**. Sayılara odaklanmak etkinliği "işe" çevirdi ve özsel motivasyonu zayıflattı ([Etkin, 2016](https://marketing.wharton.upenn.edu/wp-content/uploads/2016/10/Etkin-Jordan-11-12-15-Hidden-Cost.pdf)) [Orta]. İnsanlar takip araçlarını da sık sık bırakıp yeniden başlıyor ([Epstein ve ark., CHI 2016](https://library.selfresearch.org/research/beyond-abandonment-to-next-steps-understanding-and-designing-for-life-after-personal-informatics-tool-use/)). Bu bulgular üç tasarım kararına işaret ediyor:

- Oturum sırasında sayıları gizleyen bir "minimal mod". Sayılar yalnızca gözden geçirme anında görünür.
- N gün aradan sonra suçlamayan bir "tekrar hoş geldin" akışı.
- Motivasyonun düşük olduğu dönemler için yalnızca başlat/durdur kaydeden bir "hafif mod".

### Streak'ler, ödüller ve oyunlaştırma: iki ucu keskin

Yedi çalışmada kesintisiz bir streak sonraki katılımı artırdı. **Kırılan streak ise kırılma kişinin elinde olmayan nedenlerle olsa bile** devam etme isteğini düşürdü. Etki, kişi kendini sorumlu hissettiğinde büyüdü, **streak'i "onarma" imkânı olduğunda ise azaldı** ([Silverman & Barasch, 2023](https://udspace.udel.edu/items/42ce576b-8e1f-429a-8541-e29e48dbcfbb/full)) [Orta].

61.000'den fazla spor salonu üyesiyle 54 dijital programın test edildiği "megastudy"de en etkili bileşen, **kaçırılan bir antrenmandan sonra geri dönmeye verilen küçük bir bonus** oldu. Bu bonus haftalık ziyaretleri ~%27 artırdı. Ancak müdahalelerin yalnızca ~%8'i dört haftalık süre bittikten sonra da ölçülebilir bir etki bıraktı ([Milkman ve ark., 2021](https://penntoday.upenn.edu/news/wharton-study-best-ways-boost-workout-habits)) [Güçlü; RKÇ].

Yeni hafta, yeni ay ve yeni dönem gibi zamansal dönüm noktalarından sonra hedefe yönelik davranışlar artıyor ([Dai, Milkman & Riis, 2014](https://faculty.wharton.upenn.edu/wp-content/uploads/2014/06/Dai_Fresh_Start_2014_Mgmt_Sci.pdf)). Bu "taze başlangıç" etkisi, haftalık gözden geçirmeyi pazartesiye koymak için iyi bir gerekçe.

Ödül ve oyunlaştırma tarafında üç bulgu var:

- Beklenen somut ödüller özsel motivasyonu düşürüyor: katılıma bağlı ödülde d = −0,40, tamamlamaya bağlı ödülde d = −0,36 ([Deci, Koestner & Ryan, 1999](https://home.ubalt.edu/ntygmitc/642/Articles%20syllabus/Deci%20Koestner%20Ryan%20meta%20IM%20psy%20bull%2099.pdf)) [Güçlü; Cameron & Pierce tarafından tartışmalı]. Aynı makaleye göre sözel, yetkinliği onaylayan geri bildirim ise özsel motivasyonu artırma eğiliminde.
- Oyunlaştırmanın öğrenme üzerindeki etkisi küçük ve pozitif: bilişsel çıktılarda g = 0,49, motivasyonda g = 0,36, davranışta g = 0,25. Motivasyonel ve davranışsal etkiler yüksek kaliteli çalışmalarda daha az kararlı ([Sailer & Homner, 2020](https://link.springer.com/article/10.1007/s10648-019-09498-w)) [Güçlü].
- "Ayartma paketlemesi" de işe yarıyor ama etkisi zamanla sönüyor. Spor salonunda sevilen sesli kitapları yalnızca salonda dinlemek ziyaretleri başta %51 artırdı, ancak bu etki zamanla azaldı ([Milkman, Minson & Volpp, 2014](https://repository.upenn.edu/oid_papers/150)) [Orta; saha RKÇ'si].

### Disiplinli kullanım biçimi: bir sentez

Bu bulguların birleşimi şöyle bir kullanım biçimi öneriyor:

1. **Sabit bir bağlam ve saat seç.** Her gün aynı yerde ve aynı saat aralığında, bir "çapa" eylemiyle (ör. kahveden sonra) başla.
2. **Bir eğer-ise planı yaz** ve tek bir engel planı ekle.
3. **Haftalık, spesifik ve kalibre edilmiş bir hedef koy.** Takip edilen süreyi bu hedefe göre gör.
4. **Oturumu DND açık başlat.** Ayartmayla savaşma, ondan kaçın.
5. **Her oturumu tek tıkla kaydet:** odak puanı ve gerekiyorsa tek satırlık bir not.
6. **Streak yerine "7 günün 5'i" mantığıyla çalış.** Kaçırdığın günden sonra kendini suçlama, geri dönüşü kutla.
7. **Pazartesi tahmin ile gerçeği karşılaştıran kısa bir gözden geçirme yap:** ne işe yaradı, ne engel oldu, gelecek haftanın eğer-ise planı ne.
8. **66 günü bir vaat olarak değil, gerçekçi bir beklenti olarak gör.**

Bu reçete birleşik halde test edilmedi. Her adım ayrı bir kanıta dayanıyor.

---

## 4. Pomodoro'nun kanıtlanmış yararı ruh hali; hatası ise yalnızca zamanlayıcı olarak kullanılması

### Doğrudan kanıt: az, küçük ve tek oturumluk

Pomodoro'yu doğrudan test eden kanıt sınırlı: N ≈ 87–176 arası birkaç küçük çalışma, neredeyse tamamı üniversite öğrencileriyle ve tek bir çalışma oturumunda yapılmış.

**Biwer ve ark. (2023)** 87 Hollandalı öğrenciyi gerçek bir öz-çalışma gününde üç gruba ayırdı ([Maastricht CRIS](https://cris.maastrichtuniversity.nl/en/publications/understanding-effort-regulation-comparing-pomodoro-breaks-and-sel); [PubMed](https://pubmed.ncbi.nlm.nih.gov/36859717/)) [Orta; saha RKÇ'si, tek gün]:

- Molayı kendi belirleyenler (n = 35)
- 24 dk çalışma + 6 dk mola (n = 25)
- 12 dk çalışma + 3 dk mola (n = 27)

Molayı kendi belirleyenler daha uzun çalışma blokları ve daha uzun molalar yaptı. Her iki sabit gruba göre **daha fazla yorgunluk ve dikkat dağınıklığı, daha az konsantrasyon ve motivasyon** bildirdiler. **Harcanan zihinsel çaba ve görev tamamlama ise farklı değildi.** Yazarlar sabit molaları "daha verimli" olarak nitelendiriyor, çünkü daha az çalışma süresiyle benzer tamamlama sağlandı. Bazı popüler yazılar bu sonucu "Pomodoro çıktıyı artırdı" diye çarpıtıyor. Kaynaklar arasında künye de çelişiyor: 93(S2):353–367 ile 93(3):1096–1113. DOI ise 10.1111/bjep.12593.

**Smits, Wenzel & de Bruin (2025)** iki saatlik çevrimiçi bir oturumda 94 öğrenciyi üç gruba ayırdı: serbest mola (n = 25), uzun molası olmayan 4×25/5 Pomodoro (n = 36) ve Flowtime (n = 33). Zaman içinde **yorgunluk Pomodoro'da daha hızlı arttı**. Motivasyon Pomodoro ve Flowtime'da daha hızlı düştü. Genel ortalamalar ise farklı değildi. Görev tamamlama sırasıyla %70, %69 ve %67, akış (flow) puanı 4,22, 4,10 ve 3,98 çıktı ([PMC12292963](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/)) [Orta]. Görev tamamlamayı yalnızca öznel verimlilik öngördü. Akışı ise öznel verimlilik ve **planlanan görev sayısı** öngördü.

Yazarların kendi belirttiği sınırlamalar ağır: tek maddelik ölçümler, büyük çoğunluğu kadın psikoloji öğrencilerinden oluşan homojen örneklem ve **mola içeriğinin kaydedilmemesi**. Sonuçları, hiçbir tekniğin ötekine tercih edilmemesi gerektiği. Bu makalenin ön-baskısı Flowtime'da yorgunluğun daha *yavaş* arttığını raporluyordu. Hakemli sürüm ise yukarıdaki bulguyu veriyor ([Preprints.org](https://www.preprints.org/manuscript/202503.0845/v1)). Bu rapor hakemli sürümü esas alıyor.

Diğer kaynaklar daha da zayıf:

- 176 öğrencili bir 2026 çalışmasında öz-düzenlemeli grubun daha iyi enerji bildirdiği iddia ediliyor, ama makaleye erişilemedi ([MDPI 2026](https://www.mdpi.com/2076-328X/16/7/1158)) [Doğrulanmadı].
- Popüler sitelerde "meta-analiz" diye anılan ve "çalışmaların %88'i olumlu" diye alıntılanan kaynak aslında yalnızca ~3 RKÇ içeren bir **kapsam derlemesi** ([Ogut, 2025](https://link.springer.com/article/10.1186/s12909-025-08001-0)). %88 rakamı abartılı görünüyor.

### Mola araştırmasından genel çıkarım

Daha geniş mola araştırması da tabloyu tamamlıyor. 22 örneklem ve 2.335 katılımcılık mikro-mola (≤ 10 dk) meta-analizinde molalar **dinçliği artırdı (d = 0,36)** ve **yorgunluğu azalttı (d = 0,35)**. Genel performans etkisi ise **anlamlı değildi (d = 0,16; p = 0,116)**. Performans kazancı yalnızca bilişsel yükü düşük rutin işlerde görüldü ve **daha uzun molalar daha büyük performans kazancıyla** ilişkiliydi ([Albulescu ve ark., 2022](https://doaj.org/article/c6f37b6ba159469296b2cb968b65505f)) [Güçlü; Pomodoro'ya özgü değil].

Bu kanıtın en savunulabilir özeti şu: **sabit molalar, aksi halde molayı atlayan ya da molası uzayan insanlara yardım ediyor.** Ne zaman mola verileceğine karar vermek kendi başına bir çaba ve sabit program bu kararı dışarı devrediyor. Bu bir düzenleme ve ruh hali yararı, kanıtlanmış bir çıktı yararı değil. 25/5'in başka sabit aralıklardan üstün olduğunu gösteren bir çalışma yok. Biwer'de 12/3 ile 24/6 benzer sonuç verdi. Denemelerin hiçbiri Cirillo'nun tam yöntemini (tahmin, kesinti kaydı, gün sonu işleme) test etmedi. Yalnızca mola programını test ettiler.

### Mekanizma iddiaları: hangisi tutuyor?

| İddia | Durum | Kaynak |
|---|---|---|
| Kısa molalar dikkat azalmasını (vigilance decrement) önler (hedef alışması) | **Tartışmalı.** Orijinal bulguyu N = 498'lik bir çalışma tekrarlayamadı. Kaynak/yorgunluk açıklaması daha güçlü | [Ariga & Lleras, 2011](https://pubmed.ncbi.nlm.nih.gov/21211793/); [Helton ve ark., 2015](https://interruptions.net/literature/Helton-Cognition15.pdf) |
| Moladan sonra performans en iyi *dinlenmeden* sonra, en kötü kesintisiz çalışmadan sonra | **Destekleniyor.** Aynı zihinsel kaynağı kullanan bir mola daha az işe yarıyor | [Helton ve ark., 2015](https://interruptions.net/literature/Helton-Cognition15.pdf) |
| Mola "irade pilini" doldurur (ego tükenmesi) | **Zayıf.** RRR'de d = 0,04 | [Hagger ve ark., 2016](https://kops.uni-konstanz.de/entities/publication/b014f185-b8d7-4fb7-85de-173bc46581f1) |
| Yarım kalan iş daha iyi hatırlanır (Zeigarnik) | **Tutmadı.** Genel bir bellek avantajı yok. Yarım işe *geri dönme* eğilimi (Ovsiankina) ise genel görünüyor | [Ghibellini & Meier, 2025](https://ideas.repec.org/a/pal/palcom/v12y2025i1d10.1057_s41599-025-05000-w.html) |
| Pomodoro ertelemeyi azaltır | **Doğrudan test edilmedi.** Popüler iddia | — |
| Telefonla geçirilen mola dinlendirir | **Hayır.** Telefon molası hiç mola vermemek kadar tüketiyor: %19 daha uzun süre, %22 daha az çözülen problem | [Kang & Kurtzberg, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC7044622) |

Cirillo'nun kendi gerekçesi bilişsel kaynaklar değil, **zaman kaygısı**. "Oluş" (becoming) diye adlandırdığı kaygı yaratan zaman algısının yerine ardışık, ölçülebilir zaman koymayı amaçlıyor ([Cirillo PDF, s. 3–7](https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf)). Dürüst bir çerçeveleme şu üç işlevi öne çıkarır: Pomodoro zamanlayıcısı (a) başlamayı kolaylaştıran bir taahhüt aracı, (b) mola kararını dışarı devreden bir mekanizma, (c) bir **ölçüm aracı**. Bilimsel olarak ayarlanmış bir dikkat optimumu değil.

### Belgelenmiş dezavantajlar

Belgelenmiş dezavantajlar mütevazı ama gerçek:

- **Oturum içinde daha hızlı yorgunluk.** Uzun molasız Pomodoro'da 120. dakikaya gelindiğinde yorgunluk Flowtime'dan anlamlı derecede yüksekti (Smits 2025).
- **Zor bilişsel işte sınırlı performans yararı.** Mikro-molaların performans kazancı yoğun işte görülmedi (Albulescu 2022).
- **Zil kaygısı.** Cirillo, öz-disipline alışık olmayanlarda, dış denetimden korkanlarda ve "yeterince hızlı mıyım?" diye düşünen sonuç odaklı kişilerde "Ring Anxiety" görüldüğünü kabul ediyor.
- **Araca bağımlılık.** Cirillo'ya göre ana dezavantaj, küçük bir mekanik nesneden yardım almayı kabul etmek. Teknik bırakılınca yararların çoğu kayboluyor ([Cirillo PDF, s. 26, 29](https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf)).
- **Zilin kendisi bir kesinti olabilir.** Kesintiler çıktı sabit kalsa bile stresi artırıyor (Mark 2008). Bunun Pomodoro zili için de geçerli olduğu bir çıkarım, test edilmedi.

"Pomodoro akışı (flow) öldürür" iddiası makul ama **test edilmedi**. Ölçen tek çalışma (Smits 2025) akışta fark bulmadı. Cirillo'nun ekipleri de başlangıçta 25 dakikayı kısa buldu. Kendi süresini seçen ekipler 60 dk, 2 saat, 45 dk ve 10 dk denedikten sonra 30 dakikada (25 + 5) karar kıldı. Cirillo idealin 20–35 dakika, en fazla 40 dakika olduğunu söylüyor ([Cirillo PDF, s. 24](https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf)).

### Hatalı kullanım: zamanlayıcıyı yöntem sanmak

Cirillo'nun yöntemi bir 25/5 zamanlayıcısı değil, beş aşamalı günlük bir süreç: **Planlama, Takip, Kayıt, İşleme, Görselleştirme**. Yöntemde üç kâğıt araç var: Bugün Yapılacaklar, Etkinlik Envanteri ve Kayıtlar. Hedefler artan sırayla şöyle: bir işin ne kadar çaba gerektirdiğini öğrenmek, kesintileri azaltmak, çabayı tahmin etmek, pomodoroyu daha etkili kılmak, bir zaman çizelgesi kurmak ve kişisel bir hedef belirlemek ([Cirillo PDF, s. 4–5](https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf); [U. Waterloo özeti](https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf)). Yaygın hatalar bu kuralların her birini ihlal ediyor:

| Hatalı kullanım | Cirillo'nun kuralı | MFDP karşılığı / öneri |
|---|---|---|
| Kesintide **duraklatıp devam etmek** | "Pomodoro bölünemez." Kesin kesintide pomodoro **geçersiz** sayılır ve baştan başlanır | MFDP şu an duraklatmaya izin veriyor. Pomodoro modunda varsayılan "geçersiz say/terk et" olabilir, duraklatma Free Timer'a bırakılabilir. Geçersiz pomodorolar ayrı kaydedilir, sayılmaz |
| Zilden sonra "birkaç dakika daha" çalışmak, molayı atlamak | Buna izin yok. Kısa mola 3–5 dakika | Molanın otomatik başlaması, mola uyumunun ölçülmesi |
| İş erken bitince pomodoroyu kesmek | "Başlayan pomodoro çalmalı." Kalan süre tekrar ve iyileştirmeyle (overlearning) geçirilir. İstisna: ilk 5 dakikada biten iş | Erken bitişte bir tekrar istemi |
| Uzun molayı atlamak ya da baskı altında kısaltmak | Her 4 pomodoroda (3–5 arası) 15–30 dk. Baskı altında molayı kısaltmak "ciddi bir hata" | Uzun molanın varsayılan olması. 30 dakikayı aşınca uyarı |
| Molada zihinsel efor (iş konuşması, önemli e-posta, telefon) | Kısa molada önemli zihinsel çaba yok. Uzun molada da karmaşık iş yok | "Ekrandan uzaklaş" istemi. Kang & Kurtzberg telefon molasının dinlendirmediğini gösteriyor |
| Kesintileri kaydetmemek | İç kesinti için kesme işareti ('), dış kesinti için tire (−). Dış kesintide "bilgilendir, pazarlık et, geri ara". Not: ikincil kaynaklar hangi işaretin hangi tür olduğunda çelişiyor | Duraklatmada iç/dış seçimi. Zamanlayıcıyı durdurmayan tek tuşlu kesinti kaydı ve "plansız" listesine not |
| Tahmin yapmamak, işi bölmemek | Gün başında tam sayıyla pomodoro tahmini. 5–7 pomodorodan büyükse böl, 1'den küçükse birleştir | Görevde tahmini pomodoro, 5–7'yi aşınca bölme önerisi (ağaç yapısı hazır), tahmin-gerçek karşılaştırması |
| Bir pomodoroda birden fazla görev | Pomodoro bir göreve aittir. Tek istisna 1 pomodorodan küçük işleri birleştirmek | Oturumda tek aktif görev (MFDP zaten böyle) |
| Gün sonu gözden geçirmeyi atlamak | Kayıt ve işleme günde en fazla 1 pomodoro sürer | Gün paneline kısa bir gözden geçirme adımı |
| Pomodoro sayısını gösteriş metriği yapmak | "Sayının önemi yok." Amaç aynı işi süreç iyileştirmesiyle 4 yerine 2 pomodoroda bitirmek. Sürdürülebilir hedef günde 10–12 | Ham sayı ve streak yerine kesinti/pomodoro, tahmin doğruluğu ve tamamlanan görev trendleri |
| Boş zaman etkinliklerinde kullanmak | Teknik boş zaman için kullanılmamalı | Etkin'in ölçmenin keyfi azalttığı bulgusuyla tutarlı |

Kaynaklar: [Cirillo PDF, s. 6–17, 21–29](https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf); [FacileThings](https://facilethings.com/blog/en/interruptions-on-pomodoro); [Kang & Kurtzberg, 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC7044622).

Bu tablonun önemli bir sonucu var: araştırma denemeleri yöntemi kısmen "hatalı" uyguluyor. Smits'te uzun mola yok ve hiçbir çalışma tahmini ya da kesinti kaydını test etmedi. Bu yüzden "Pomodoro serbest molayı geçemiyor" sonucu doğru okunduğunda **"yalnızca 25/5 zamanlaması geçemiyor"** anlamına geliyor. **Tam yöntem hâlâ test edilmedi.** MFDP'nin `AtomicAnalyzer`'ı ise Cirillo'nun "Takip" aşamasını çoğu uygulamadan iyi karşılıyor. Eksik olanlar tahmin, iç/dış kesinti ayrımı ve gün sonu işleme/görselleştirme.

---

## 5. En güçlü yöntemler kendini test etmek ve aralıklı tekrar; adı konmuş verim sistemleri ise sezgisel

### Öğrenme teknikleri: kanıt düzeyine göre

Çalışma biçimleri arasında kanıtı en güçlü olanlar "ne kadar" değil, "nasıl" sorusuna cevap verenler. On öğrenme tekniğini değerlendiren çapa derlemede yalnızca **kendini test etme (geri çağırma pratiği)** ve **aralıklı çalışma** "yüksek yarar" notu aldı ([Dunlosky ve ark., 2013 — APS](https://www.psychologicalscience.org/news/releases/which-study-strategies-make-the-grade.html)) [Güçlü].

| Teknik | Kanıt | Etki büyüklüğü | Not |
|---|---|---|---|
| Kendini test etme / geri çağırma | Güçlü | Tekrar okumaya karşı d ≈ 0,50 (Rowland); g ≈ 0,50–0,61 (Adesope) | ≥ 1 gün saklama aralığında ve geri bildirimle daha güçlü. Adesope'nin çalışma sayısı ikincil kaynaklarda çelişiyor (118 ve 188) |
| Aralıklı tekrar | Güçlü | ~0,60 (≈300 çalışma); 317 deney | En iyi aralık sınav ufkuyla büyüyor. Kısa aralık, uzun aralıktan daha zararlı |
| Serpiştirme (interleaving) | Orta, materyale bağlı | Genel g = 0,42; görsel g = 0,67; matematik g = 0,34; **kelime listesi g = −0,39** | Benzer ve ayırt etmesi zor kategorilerde işe yarıyor |
| Ayrıntılı sorgulama ("neden?") ve öz-açıklama | Orta | Sayılar bu çalışmada çıkarılmadı | Uygun durumlarda önerilebilir |
| Tekrar okuma, altını çizme, özetleme, anahtar kelime ipucu, metin için imgeleme | Düşük | — | Yaygın ama düşük yararlı |
| İkili kodlama, somut örnekler | Zayıf–Orta | Meta-analiz bulunamadı | Learning Scientists'in "altı stratejisi" içinde |

Kaynaklar: [Rowland, 2014](https://courseware.epfl.ch/assets/courseware/v1/fdde2f0aa590bf3b1324077a6bf1540c/asset-v1%3AEPFL%2BDEMO%2B2020%2Btype%40asset%2Bblock/Rowland2014-meta-analysis.pdf); [Adesope ve ark., 2017](https://journals.sagepub.com/doi/10.3102/0034654316689306); [Cepeda ve ark., 2006](https://pubmed.ncbi.nlm.nih.gov/16719566/); [Donoghue & Hattie, 2021](https://www.frontiersin.org/articles/10.3389/feduc.2021.581216/full); [Brunmair & Richter, 2019](https://www.psychologie.uni-wuerzburg.de/fileadmin/06020400/2019/Brunmair_Richter_in_press__2019_META-ANALYSIS_OF_INTERLEAVED_LEARNING.pdf).

Bunun öğrenci için önemi, bilinçli pratiğin (deliberate practice) performans varyansının oyunlarda %26'sını, müzikte %21'ini, sporda %18'ini, **eğitimde ise yalnızca %4'ünü** açıklamasıyla netleşiyor ([Macnamara, Hambrick & Oswald, 2014](https://www.sciencedaily.com/releases/2014/07/140716123835.htm)) [Güçlü; ölçüm hatası düzeltmesiyle ortalamanın ~%19'a çıktığını savunan bir yorum da var: [Hambrick ve ark., 2014](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/)]. Ham saat tek başına notu pek açıklamıyor. Bu yüzden MFDP yalnızca saati ödüllendirmemeli. "Tekrar/Test" ve "Yeni konu/Okuma" gibi oturum türleri ayırmalı ve sınav başına geri çağırma oturumlarının payını ve çalışılan farklı gün sayısını (aralıklama) göstermeli.

### Bir oturumun ve sınav takviminin önerilen yapısı

Kanıtları birleştiren ama **birleşik halde test edilmemiş** bir şablon şöyle:

**25 dakikalık bir oturum içinde:**

- İlk 3–5 dakika: önceki oturumun kapalı kitap hatırlaması.
- 15–18 dakika: "neden?" sorularıyla yeni materyal.
- Son 3–5 dakika: kendini test etme ve notlarla kontrol.
- Ardından ekrandan uzakta 5 dakika mola.

**Sınav takviminde:**

- T−4 hafta ve öncesi: konu başına kısa bir test.
- Sonrasında: kalan sürenin ~%20–25'i aralıklarla tekrar.
- T−1 hafta: konular arası karışık deneme testleri.
- T−1 gün: hafif geri çağırma ve normal yatış saati.

### İş yapılandırma: mekanizma sağlam, adı konmuş sistemler zayıf

İş yapılandırma yöntemlerinde mekanizma, adı konmuş sistemlerden daha sağlam:

- **Görev değiştirme maliyetleri** laboratuvarda sağlam. Hazırlık süresi olsa bile "kalıntı" bir maliyet kalıyor ([Monsell, 2003](https://doi.org/10.1016/S1364-6613(03)00028-7)) [Güçlü].
- **Dikkat kalıntısı**: yarım bırakılan bir işten başka işe geçenler eski işi düşünmeye devam ediyor ve yeni işteki performansları düşüyor ([Leroy, 2009](https://www.uwb.edu/faculty/?p=144)) [Orta; iki deney].
- Kesintiye uğrayan işe dönmek için kısa bir **"dönüş planı"** yapmak kalıntıyı azaltıyor ([UW haberi, 2018](https://www.washington.edu/news/2018/01/16/task-interrupted-a-plan-for-returning-helps-you-move-on/); [Leroy & Schmidt, 2016](https://ideas.repec.org/a/eee/jobhdp/v137y2016icp218-235.html)). MFDP için ucuz bir karşılığı var: duraklatmada ya da oturum sonunda tek satırlık "nerede kaldım / sıradaki adım" notu.
- Ağır medya çoklu-görevcilerinin daha büyük geçiş maliyeti gösterdiği bulgusunun ([Ophir, Nass & Wagner, 2009](https://boingboing.net/2011/11/07/eyal-ophir-on-the-science-of-multitasking.html)) replikasyonları **karışık** ([PMC5662702](https://pmc.ncbi.nlm.nih.gov/articles/PMC5662702)).

### "23 dakika" efsanesi

Çok tekrarlanan "bir kesintiden sonra odaklanmak 23 dakika sürer" iddiası bir efsane. Kaynak olarak gösterilen çalışmada tek bir şirketteki 24 bilgi çalışanı gözlemlendi. Aynı gün devam ettirilen işlere ortalama **25 dk 26 s** sonra geri dönüldü. Bu süre dış kesintiden sonra 22 dk 37 s, kendi kendini kesmeden sonra 29 dk 1 s idi. "23 dk 15 s" rakamı Mark'ın röportajlarından gelen bir yuvarlama ve makalede geçmiyor. Daha önemlisi ölçülen şey **işe geri dönme süresi, odağı yeniden kazanma süresi değil** ([Feedbagel incelemesi](https://feedbagel.com/post/investigating-the-origin-of-the-23-minute-interruption-recovery-time-claim); [Mark, Gonzalez & Harris, CHI 2005](https://doi.org/10.1145/1054972.1055017)) [Zayıf/Popüler; birincil metin bu araştırmada okunmadı]. Yine de "kendi kendini kesmeden sonra işe daha geç dönülüyor" ayrımı, MFDP'deki iç/dış kesinti ayrımının değerini bir kez daha gösteriyor.

### Adı konmuş verim sistemleri

| Yöntem | Kanıt durumu |
|---|---|
| Deep Work (Newport) | Pratisyen çerçeve [Zayıf]. "~4 saat" sınırı Ericsson'a dayandırılıyor ama makalede sert bir tavan bulunamadı |
| GTD (Allen), Eisenhower matrisi, "eat the frog", zaman bloklama | Kontrollü çalışma yok [Zayıf]. Mekanizmaları (az geçiş, planlama, eğer-ise planı) daha iyi destekleniyor |
| Flowtime (molanın çalışma süresiyle ölçeklenmesi) | Kaynakları yalnızca bloglar ([Zapier](https://zapier.com/blog/flowtime-technique.md)). Tek RKÇ'de üstünlük göstermedi (Smits 2025) |
| 52/17 | Firma (DeskTime) kullanıcılarının en "verimli" %10'unun gözlemsel verisi. Firmanın 2021 tekrarında oran 112/26 çıktı ve 52/17 tutmadı ([DeskTime](https://desktime.com/blog/52-17); [Silicon Canals](https://siliconcanals.com/t-desktime-52-17-work-break-productivity-observational-data/)) [Zayıf] |
| 90 dakikalık ultradiyen döngü (Kleitman BRAC) | BRAC yalnızca **uykuda** iyi kurulmuş. Uyanıklıkta varlığı 1977'den beri sorgulanıyor ([Nature 1977](https://www.nature.com/articles/265360a0.pdf); [Wikipedia: BRAC](https://en.wikipedia.org/wiki/Basic_rest%E2%80%93activity_cycle)). Çalışma bloklarına uygulanması için güvenilir bir kaynak bulunamadı [Zayıf] |
| 50/10 | Hiç çalışma bulunamadı |
| "Öğle sonrası düşüş" (post-lunch dip) | Yaygın olarak bildiriliyor ama bu araştırmada kaynak alınamadı [Doğrulanmadı] |

Bu tablonun sonucu: kanıt **bir mola yapısına sahip olmayı** destekliyor, belirli bir oranı değil. Çalışma süreleri yapılandırılabilir olmalı. Cirillo'nun 20–40 dakikalık pomodoro aralığı ve derin iş için daha uzun Free Timer/Flowtime blokları sunulmalı. Flowtime molası çalışma süresinin ~1/5–1/3'ü olarak önerilebilir. Doğru aralık kişinin kendi verisinden önerilmeli.

---

## Sonuç

Bu araştırmanın değiştirdiği temel bakış şu: MFDP'nin değeri "Pomodoro'yu doğru zamanlaması" değil, **Cirillo'nun unutulan yarısını, yani ölçme, tahmin ve gözden geçirmeyi, davranış bilimi literatürünün en sağlam bulgularıyla birleştirebilmesi**. Literatürde Pomodoro zamanlayıcısının tek başına çıktıyı artırdığına dair kanıt yok. İzlemenin (d ≈ 0,40), eğer-ise planlarının (d ≈ 0,65), geri çağırma ve aralıklı tekrarın (≈ 0,5–0,6) ve tahminleri geçmiş veriye bağlamanın etkisi ise bağımsız olarak gösterilmiş durumda. Bu araçların hepsi MFDP'nin zaten tuttuğu veriyle ya da tek tıklık eklemelerle (odak puanı, iç/dış kesinti, görev başına tahmin) çalışabiliyor. Paradoksal biçimde en büyük risk de verinin kendisinden geliyor. Ham pomodoro sayısı, katı streak'ler ve sürekli görünen sayaçlar Goodhart yasası, kırılan streak etkisi ve ölçmenin keyfi azaltması yoluyla ters tepebilir. İyi tasarım, metriği hedef olmaktan çıkarıp **geri bildirim** olarak konumlandırıyor.

İkinci çıkarım, MFDP'nin bu alandaki gerçek bilinmeyenleri test etmek için alışılmadık derecede uygun bir araç olması. Cirillo'nun tam yöntemi (geçersiz sayma, kesinti kaydı, tahmin, gün sonu işleme) hiçbir kontrollü çalışmada test edilmedi. Sabit ve esnek mola konusunda iki Hollanda çalışması çelişiyor. Kronotip etkisi genç yetişkinlerin yalnızca yarısından azında görülüyor. Bu boşluklar genel bir cevabın henüz olmadığını, ama **kişisel bir cevabın** kurulabileceğini gösteriyor. Kişisel deneyler için bir `experiment_id` alanı, sınav notlarını takvime bağlamak ve `focus_shift_detected`'i gizliliği koruyarak devreye almak, MFDP'yi bir zamanlayıcıdan küçük ölçekli bir kişisel araştırma platformuna dönüştürür. Bu dönüşümde dürüstlüğü korumak da önemli: "verimliliği %X artırır" gibi kanıtlanmamış vaatlerden kaçınılmalı ve kullanıcıya şu söylenmeli: "Sabit molalar öğrencilerde benzer çıktıyla daha az yorgunluk ve daha iyi konsantrasyonla ilişkili bulundu. Senin için neyin işe yaradığını verin gösterecek."

---

## Kaynakça

Kaynaklar notlar arasında birleştirildi ve tekrarlar çıkarıldı. Köşeli parantez içindeki etiket kanıt türünü gösteriyor: **[MA]** meta-analiz, **[RRR]** çok laboratuvarlı ön-kayıtlı replikasyon, **[RKÇ]** randomize/saha deneyi, **[Deney]** laboratuvar deneyi, **[Göz]** gözlemsel/korelasyonel, **[Nitel]** HCI görüşme/anket, **[Derleme]**, **[Kitap/Birincil]**, **[Firma/Blog]**. Araştırmacıların bazı künye ayrıntılarını (sayfa aralıkları, DOI'ler) kendi bilgisinden verdiği belirtilmiştir. Bunlar yayından önce kontrol edilmeli.

### A. Hakemli akademik kaynaklar

1. Adesope, O. O., Trevisan, D. A., & Sundararajan, N. (2017). Rethinking the use of tests: A meta-analysis of practice testing. *Review of Educational Research, 87*(3), 659–701. https://doi.org/10.3102/0034654316689306 [MA]
2. Albulescu, P., Macsinga, I., Rusu, A., Sulea, C., Bodnaru, A., & Tulbure, B. T. (2022). "Give me a break!" A systematic review and meta-analysis on the efficacy of micro-breaks for increasing well-being and performance. *PLOS ONE, 17*(8), e0272460. https://doi.org/10.1371/journal.pone.0272460 [MA]
3. Ariely, D., & Wertenbroch, K. (2002). Procrastination, deadlines, and performance: Self-control by precommitment. *Psychological Science, 13*(3). https://stafforini.com/works/ariely-2002-procrastination-deadlines-performance/ [Deney; bkz. #33 replikasyon]
4. Ariga, A., & Lleras, A. (2011). Brief and rare mental "breaks" keep you focused: Deactivation and reactivation of task goals preempt vigilance decrements. *Cognition, 118*(3), 439–443. https://pubmed.ncbi.nlm.nih.gov/21211793/ [Deney; tartışmalı]
5. Biwer, F., Wiradhany, W., oude Egbrink, M. G. A., & de Bruin, A. B. H. (2023). Understanding effort regulation: Comparing 'Pomodoro' breaks and self-regulated breaks. *British Journal of Educational Psychology, 93*(S2), 353–367. https://doi.org/10.1111/bjep.12593 [RKÇ; sayı/sayfa künyesi kaynaklar arasında çelişiyor]
6. Brunmair, M., & Richter, T. (2019). Similarity matters: A meta-analysis of interleaved learning and its moderators. *Psychological Bulletin, 145*(11), 1029–1052. https://doi.org/10.1037/bul0000209 [MA]
7. Buehler, R., Griffin, D., & Ross, M. (1994). Exploring the "planning fallacy": Why people underestimate their task completion times. *Journal of Personality and Social Psychology, 67*(3), 366–381. https://doi.org/10.1037/0022-3514.67.3.366 [Deney]
8. Cepeda, N. J., Pashler, H., Vul, E., Wixted, J. T., & Rohrer, D. (2006). Distributed practice in verbal recall tasks: A review and quantitative synthesis. *Psychological Bulletin, 132*(3), 354–380. https://pubmed.ncbi.nlm.nih.gov/16719566/ [MA]
9. Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., & Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. *Psychological Science, 19*(11), 1095–1102. https://pubmed.ncbi.nlm.nih.gov/19076480/ [Deney]
10. Chauhan, S., ve ark. (2025). Chronotype and synchrony effects in human cognitive performance: A systematic review. *Chronobiology International, 42*(4), 463–499. https://doi.org/10.1080/07420528.2025.2490495 [Derleme]
11. Cross, A., & Sheffield, D. (2019). Mental contrasting for health behaviour change: A systematic review and meta-analysis of effects and moderator variables. *Health Psychology Review, 13*(2), 209–225. https://pubmed.ncbi.nlm.nih.gov/30879403/ [MA]
12. Dabbish, L., Mark, G., & González, V. M. (2011). Why do I keep interrupting myself? Environment, habit and self-interruption. *Proceedings of CHI 2011*. https://isr.uci.edu/node/1353.html [Göz]
13. Dai, H., Milkman, K. L., & Riis, J. (2014). The fresh start effect: Temporal landmarks motivate aspirational behavior. *Management Science, 60*(10), 2563–2582. https://doi.org/10.1287/mnsc.2014.1901 [Göz; arşiv saha verisi]
14. Deci, E. L., Koestner, R., & Ryan, R. M. (1999). A meta-analytic review of experiments examining the effects of extrinsic rewards on intrinsic motivation. *Psychological Bulletin, 125*(6), 627–668. https://doi.org/10.1037/0033-2909.125.6.627 [MA]
15. Deci, E. L., Koestner, R., & Ryan, R. M. (2001). Extrinsic rewards and intrinsic motivation in education: Reconsidered once again. *Review of Educational Research, 71*(1), 1–27. https://doi.org/10.3102/00346543071001001 [Derleme]
16. de Ridder, D. T. D., Lensvelt-Mulders, G., Finkenauer, C., Stok, F. M., & Baumeister, R. F. (2012). Taking stock of self-control: A meta-analysis of how trait self-control relates to a wide range of behaviors. *Personality and Social Psychology Review, 16*(1), 76–99. https://doi.org/10.1177/1088868311418749 [MA; Galla & Duckworth üzerinden aktarıldı]
17. Donoghue, G. M., & Hattie, J. A. C. (2021). A meta-analysis of ten learning techniques. *Frontiers in Education, 6*, 581216. https://doi.org/10.3389/feduc.2021.581216 [MA]
18. Dunlosky, J., Rawson, K. A., Marsh, E. J., Nathan, M. J., & Willingham, D. T. (2013). Improving students' learning with effective learning techniques. *Psychological Science in the Public Interest, 14*(1), 4–58. https://doi.org/10.1177/1529100612453266 [Derleme]
19. Epstein, D. A., Ping, A., Fogarty, J., & Munson, S. A. (2015). A lived informatics model of personal informatics. *Proceedings of UbiComp 2015*, 731–742. https://doi.org/10.1145/2750858.2804250 [Nitel]
20. Epstein, D. A., Caraway, M., Johnston, C., Ping, A., Fogarty, J., & Munson, S. A. (2016). Beyond abandonment to next steps: Understanding and designing for life after personal informatics tool use. *Proceedings of CHI 2016*, 1109–1113. https://doi.org/10.1145/2858036.2858045 [Nitel]
21. Ericsson, K. A., Krampe, R. T., & Tesch-Römer, C. (1993). The role of deliberate practice in the acquisition of expert performance. *Psychological Review, 100*(3), 363–406. https://doi.org/10.1037/0033-295X.100.3.363 [Göz]
22. Etkin, J. (2016). The hidden cost of personal quantification. *Journal of Consumer Research, 42*(6), 967–984. https://doi.org/10.1093/jcr/ucv095 [Deney]
23. Galla, B. M., & Duckworth, A. L. (2015). More than resisting temptation: Beneficial habits mediate the relationship between self-control and positive life outcomes. *Journal of Personality and Social Psychology, 109*(3), 508–525. https://doi.org/10.1037/pspp0000026 [Göz; boylamsal]
24. Ghibellini, R., & Meier, B. (2025). The hypothesis of the Zeigarnik effect: A meta-analysis (başlık kayda göre). *Humanities and Social Sciences Communications, 12*. https://doi.org/10.1057/s41599-025-05000-w [MA]
25. Gollwitzer, P. M., & Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. *Advances in Experimental Social Psychology, 38*, 69–119. https://doi.org/10.1016/S0065-2601(06)38002-1 [MA]
26. Hagger, M. S., Chatzisarantis, N. L. D., ve ark. (2016). A multilab preregistered replication of the ego-depletion effect. *Perspectives on Psychological Science, 11*(4), 546–573. https://doi.org/10.1177/1745691616652873 [RRR]
27. Hambrick, D. Z., Altmann, E. M., Oswald, F. L., Meinz, E. J., Gobet, F., & Campitelli, G. (2014). Facing facts about deliberate practice. *Frontiers in Psychology, 5*, 751. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4101876/ [Yorum]
28. Harkin, B., Webb, T. L., Chang, B. P. I., Prestwich, A., Conner, M., Kellar, I., Benn, Y., & Sheeran, P. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence. *Psychological Bulletin, 142*(2), 198–229. https://doi.org/10.1037/bul0000025 [MA]
29. Helton, W. S., & Russell, P. N. (2012). Brief mental breaks and content-free cues may not keep you focused. *Experimental Brain Research*. https://www.springermedicine.com/brief-mental-breaks-and-content-free-cues-may-not-keep-you-focus/25692108 [Deney]
30. Helton, W. S., ve ark. (2015). *Cognition, 134*, 165–173 (dinlenme ve diğer kesintiler sonrası uyanıklık). https://interruptions.net/literature/Helton-Cognition15.pdf [Deney]
31. Hofmann, W., Baumeister, R. F., Förster, G., & Vohs, K. D. (2012). Everyday temptations: An experience sampling study of desire, conflict, and self-control. *Journal of Personality and Social Psychology, 102*(6), 1318–1335. https://doi.org/10.1037/a0026545 [Göz; ESM]
32. Hogan, M. J., ve ark. (2009). Optimal time-of-day and consolidation of learning in younger and older adults. https://hasherlab.psych.utoronto.ca/PDF/2009%20(Hogan%20et%20al.)%20Optimal%20time-of-day%20and%20consolidation%20of%20learning%20in%20younger%20and%20older%20adult.pdf [Deney]
33. Hyndman, K., & Bisin, A. (2026). Replication of Ariely & Wertenbroch (2002) Study 2. *Psychological Science*. https://journals.sagepub.com/doi/full/10.1177/09567976261460772 [Replikasyon]
34. Kang, S., & Kurtzberg, T. R. (2019). Reach for your cell phone at your own risk: The cognitive costs of media choice for breaks. *Journal of Behavioral Addictions, 8*(3), 395–403. https://pmc.ncbi.nlm.nih.gov/articles/PMC7044622 [RKÇ]
35. Karkar, R., Schroeder, J., Epstein, D. A., ve ark. (2017). TummyTrials: A feasibility study of using self-experimentation to detect individualized food triggers. *Proceedings of CHI 2017*. https://pmc.ncbi.nlm.nih.gov/articles/PMC5432136 [Fizibilite]
36. Kim, Y.-H., Jeon, J. H., Choe, E. K., Lee, B., Kim, K., & Seo, J. (2016). TimeAware: Leveraging framing effects to enhance personal productivity. *Proceedings of CHI 2016*, 272–283. https://terpconnect.umd.edu/~choe/download/CHI-2016-Kim-TimeAware.pdf [Saha deneyi]
37. Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W., & Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. *European Journal of Social Psychology, 40*(6), 998–1009. https://doi.org/10.1002/ejsp.674 [Göz; küçük örneklem, replike edilmedi]
38. Leroy, S. (2009). Why is it so hard to do my work? The challenge of attention residue when switching between work tasks. *Organizational Behavior and Human Decision Processes, 109*(2), 168–181. https://doi.org/10.1016/j.obhdp.2009.04.002 [Deney]
39. Leroy, S., & Schmidt, A. M. (2016). The effect of regulatory focus on attention residue and performance during interruptions. *Organizational Behavior and Human Decision Processes, 137*, 218–235. https://ideas.repec.org/a/eee/jobhdp/v137y2016icp218-235.html [Deney]
40. Locke, E. A., & Latham, G. P. (2002). Building a practically useful theory of goal setting and task motivation: A 35-year odyssey. *American Psychologist, 57*(9), 705–717. https://doi.org/10.1037/0003-066X.57.9.705 [Derleme]
41. Macnamara, B. N., Hambrick, D. Z., & Oswald, F. L. (2014). Deliberate practice and performance in music, games, sports, education, and professions: A meta-analysis. *Psychological Science, 25*(8), 1608–1618. https://doi.org/10.1177/0956797614535810 [MA]
42. Macnamara, B. N., Moreau, D., & Hambrick, D. Z. (2016). The relationship between deliberate practice and performance in sports: A meta-analysis. *Perspectives on Psychological Science, 11*(3), 333–350. https://hhs.purdue.edu/skill-learning-and-performance-lab/wp-content/uploads/sites/43/2024/08/macnamara-et-al-2016-the-relationship-between-deliberate-practice-and-performance-in-sports-a-meta-analysis.pdf [MA]
43. Mark, G., Gonzalez, V. M., & Harris, J. (2005). No task left behind? Examining the nature of fragmented work. *Proceedings of CHI 2005*, 321–330. https://doi.org/10.1145/1054972.1055017 [Göz; birincil metin bu araştırmada okunmadı]
44. Mark, G., Gudith, D., & Klocke, U. (2008). The cost of interrupted work: More speed and stress. *Proceedings of CHI 2008*, 107–110. https://www.interruptions.net/literature/Mark-CHI08.pdf [Deney]
45. Mark, G., Iqbal, S. T., Czerwinski, M., & Johns, P. (2014). Bored Mondays and focused afternoons: The rhythm of attention and online activity in the workplace. *Proceedings of CHI 2014*, 3025–3034. https://isr.uci.edu/node/2035.html [Göz]
46. Mark, G., Iqbal, S. T., Czerwinski, M., Johns, P., & Sano, A. (2016). Neurotics can't focus: An in situ study of online multitasking in the workplace. *Proceedings of CHI 2016*, 1739–1744. https://www.microsoft.com/en-us/research/?p=238240 [Göz]
47. May, C. P., Hasher, L., & Stoltzfus, E. R. (1993). Optimal time of day and the magnitude of age differences in memory. *Psychological Science, 4*(5), 326–330. https://hasherlab.psych.utoronto.ca/abstracts/may_etal_93.htm [Deney]
48. Meyer, A. N., ve ark. (2018). Design recommendations for self-monitoring in the workplace: Studies in software development. *PACM HCI (CSCW 2018)*. https://www.merlin.uzh.ch/publication/show/15499 [Saha çalışması]
49. Milkman, K. L., Minson, J. A., & Volpp, K. G. M. (2014). Holding the Hunger Games hostage at the gym: An evaluation of temptation bundling. *Management Science, 60*(2), 283–299. https://doi.org/10.1287/mnsc.2013.1784 [RKÇ]
50. Milkman, K. L., ve ark. (2021). Megastudies improve the impact of applied behavioural science. *Nature, 600*, 478–483. https://doi.org/10.1038/s41586-021-04128-4 [RKÇ; megastudy]
51. Monsell, S. (2003). Task switching. *Trends in Cognitive Sciences, 7*(3), 134–140. https://doi.org/10.1016/S1364-6613(03)00028-7 [Derleme]
52. Ogut, E. (2025). Pomodoro technique in (anatomy/medical) education: Scoping review. *BMC Medical Education*. https://doi.org/10.1186/s12909-025-08001-0 [Kapsam derlemesi; meta-analiz değil]
53. Okano, K., Kaczmarzyk, J. R., Dave, N., Gabrieli, J. D. E., & Grossman, J. C. (2019). Sleep quality, duration, and consistency are associated with better academic performance in college students. *npj Science of Learning, 4*, 16. https://doi.org/10.1038/s41539-019-0055-z [Göz]
54. Ophir, E., Nass, C., & Wagner, A. D. (2009). Cognitive control in media multitaskers. *PNAS, 106*(37), 15583–15587. https://doi.org/10.1073/pnas.0903620106 [Deney; replikasyonlar karışık, bkz. https://pmc.ncbi.nlm.nih.gov/articles/PMC5662702]
55. Rowland, C. A. (2014). The effect of testing versus restudy on retention: A meta-analytic review of the testing effect. *Psychological Bulletin, 140*(6), 1432–1463. https://doi.org/10.1037/a0037559 [MA]
56. Sailer, M., & Homner, L. (2020). The gamification of learning: A meta-analysis. *Educational Psychology Review, 32*(1), 77–112. https://doi.org/10.1007/s10648-019-09498-w [MA]
57. Schmidt, C., Collette, F., Cajochen, C., & Peigneux, P. (2007). A time to think: Circadian rhythms in human cognition. *Cognitive Neuropsychology, 24*(7), 755–789. https://orbi.uliege.be/handle/2268/4666 [Derleme]
58. Silverman, J., & Barasch, A. (2023). On or off track: How (broken) streaks affect consumer decisions. *Journal of Consumer Research, 49*(6), 1095–1117. https://doi.org/10.1093/jcr/ucac029 [Deney; 7 çalışma]
59. Smits, E. J. C., Wenzel, N., & de Bruin, A. (2025). Investigating the effectiveness of self-regulated, Pomodoro, and Flowtime break-taking techniques among students. *Behavioral Sciences, 15*(7), 861. https://pmc.ncbi.nlm.nih.gov/articles/PMC12292963/ (ön-baskı: https://www.preprints.org/manuscript/202503.0845/v1) [RKÇ]
60. Steel, P. (2007). The nature of procrastination: A meta-analytic and theoretical review of quintessential self-regulatory failure. *Psychological Bulletin, 133*(1), 65–94. https://doi.org/10.1037/0033-2909.133.1.65 [MA]
61. Wang, G., Wang, Y., & Gai, X. (2021). A meta-analysis of the effects of mental contrasting with implementation intentions on goal attainment. *Frontiers in Psychology, 12*, 565202. https://doi.org/10.3389/fpsyg.2021.565202 [MA]
62. Wiehler, A., Branzoli, F., Adanyeguh, I., Mochel, F., & Pessiglione, M. (2022). A neuro-metabolic account of why daylong cognitive work alters the control of economic decisions. *Current Biology, 32*(16), 3564–3575. https://hal.sorbonne-universite.fr/hal-04534917 [Deney]
63. Wood, W., & Neal, D. T. (2007). A new look at habits and the habit–goal interface. *Psychological Review, 114*(4), 843–863. https://dornsife.usc.edu/wendy-wood/wp-content/uploads/sites/183/2023/10/wood.neal_.2007psychrev_a_new_look_at_habits_and_the_interface_between_habits_and_goals.pdf [Kuram/Derleme]
64. Wood, W., Tam, L., & Guerrero Witt, M. (2005). Changing circumstances, disrupting habits. *Journal of Personality and Social Psychology, 88*(6), 918–933. [Yalnızca künye; içerik alınamadı]
65. Züger, M., ve ark. (2017). Reducing interruptions at work: A large-scale field study of FlowLight. *Proceedings of CHI 2017*. https://doi.org/10.1145/3025453.3025662 [Saha çalışması, n = 449]

### B. Kitaplar ve birincil yöntem metinleri

66. Allen, D. (2001/2015). *Getting Things Done*. Penguin. [Kitap; paket olarak ampirik test edilmedi]
67. Cirillo, F. (2006/2007). *The Pomodoro Technique* (v1.0, 19 Ekim 2006; v1.3, 15 Haziran 2007), CC BY-NC-ND 3.0. https://www.faasafety.gov/files/events/SO/SO15/2024/SO15134204/Cirillo_--_Pomodoro_Technique.pdf [Birincil]
68. Cirillo, F. (2018). *The Pomodoro Technique*. Currency/Crown. https://www.penguinrandomhouse.com/books/555557/the-pomodoro-technique-by-francesco-cirillo/ [Kitap; 2007 PDF'ten farkları doğrulanmadı]
69. Mark, G. (2023). *Attention Span: A Groundbreaking Way to Restore Balance, Happiness and Productivity*. Hanover Square Press. Röportaj: https://www.steelcase.com/research/articles/our-47-second-attention-span-with-gloria-mark-s5-ep3-transcript/ [Kitap]
70. Newport, C. (2016). *Deep Work: Rules for Focused Success in a Distracted World*. Grand Central Publishing. [Kitap; pratisyen]
71. University of Waterloo Writing & Communication Centre. *Cirillo's Pomodoro Technique: A Summary* (el notu). https://uwaterloo.ca/writing-and-communication-centre/sites/default/files/uploads/files/pomodoro_technique.pdf [İkincil özet]

### C. Firma verisi, uygulama dokümantasyonu ve popüler kaynaklar (düşük kanıt değeri)

72. DeskTime (2014; 2021 tekrar). The 52/17 rule / Does the 52-17 rule really hold up? https://desktime.com/blog/52-17 ; https://desktime.com/blog/?p=1264 [Firma; gözlemsel]
73. Silicon Canals. 52/17 eleştirisi. https://siliconcanals.com/t-desktime-52-17-work-break-productivity-observational-data/ [Blog]
74. Feedbagel. Investigating the origin of the 23-minute interruption recovery time claim. https://feedbagel.com/post/investigating-the-origin-of-the-23-minute-interruption-recovery-time-claim [Blog; "23 dk" efsanesinin incelenmesi]
75. Zapier. Flowtime technique. https://zapier.com/blog/flowtime-technique.md [Blog]
76. RescueTime Help Center. How is my Productivity Pulse calculated? https://help.rescuetime.com/article/73-how-is-my-productivity-pulse-calculated [Firma]
77. Rize. Weekly productivity assessment; The hidden cost of context switching. https://rize.io/blog/releasing-the-new-weekly-productivity-assessment ; https://rize.io/blog/the-hidden-cost-of-context-switching [Firma]
78. Focus To-Do, App Store kaydı. https://apps.apple.com/app/id1258530160 [Firma]
79. Meyer, A. N., ve ark. PersonalAnalytics projesi (UZH). https://www.ifi.uzh.ch/en/seal/people/meyer/personal-analytics.html [Proje sayfası]
80. FacileThings. Interruptions on Pomodoro. https://facilethings.com/blog/en/interruptions-on-pomodoro [Blog]
81. Unhustle. The 10,000-hour rule myth and the 4-hour limit. https://unhustle.substack.com/p/the-10000-hour-rule-myth-and-the [Blog]
82. Wikipedia. Basic rest–activity cycle. https://en.wikipedia.org/wiki/Basic_rest%E2%80%93activity_cycle ; ilgili eleştiri: *Nature* (1977), https://www.nature.com/articles/265360a0.pdf [Ansiklopedi + birincil eleştiri]
83. Wikipedia. Pomodoro Technique. https://en.wikipedia.org/wiki/Pomodoro_Technique [Ansiklopedi]

### D. Bu araştırmada doğrulanamayan ya da yalnızca ikincil kaynaktan bilinen kaynaklar

84. MDPI *Behavioral Sciences* (2026), 16(7), 1158. Systematic vs. self-regulated breaks during reading comprehension, N = 176. https://www.mdpi.com/2076-328X/16/7/1158 [Yazarlar ve sonuçlar doğrulanmadı; sayfa 403 döndü]
85. Meyer, A. N., Barton, L. E., Murphy, G. C., Zimmermann, T., & Fritz, T. (2017). The work life of developers: Activities, switches and perceived productivity. *IEEE TSE, 43*(12). https://doi.org/10.1109/TSE.2017.2656886 [Doğrulanmadı]
86. Weinstein, Y., Madan, C. R., & Sumeracki, M. A. (2018). Teaching the science of learning. *Cognitive Research: Principles and Implications, 3*, 2. https://doi.org/10.1186/s41235-017-0087-y [Doğrulanmadı]
87. Heylighen, F., & Vidal, C. (2008). Getting Things Done: The science behind stress-free productivity. *Long Range Planning*. [Doğrulanmadı]
88. Sheeran, P., Listrom, O., & Gollwitzer, P. M. (2024). Eğer-ise planlarının 642 testlik ipucu/yanıt taksonomisi. İkincil özet: https://goalsandprogress.com/implementation-intentions-research/ [İkincil]
89. Monk, T. H. (2005). The post-lunch dip in performance. *Clinics in Sports Medicine*. [Doğrulanmadı]
90. Kirgios, E., ve ark. (2020). 24 Hour Fitness ayartma paketlemesi takip çalışması. [Yalnızca ikincil kaynaklarda; doğrulanmadı]
