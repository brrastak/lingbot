from lingbot.translation.translation import parse, Translation


def test_parse():
    with open("./lingbot/tests/example_input.txt", 'r') as file:
        source = file.read()
    expected = Translation(translations=['(orgán sluchu) у́хо', '(ušnica) у́хо, ушна́я ра́ковина', '(na hrnci ap.) у́хо, ру́чка', '(nováčik) молокосо́с, новичо́к'], examples=[('(anat.) vnútorné/stredné/vonkajšie ucho', 'вну́треннее/сре́днее/нару́жное у́хо'), ('(med.) zápal stredného ucha', 'воспале́ние сре́днего у́ха'), ('úsmev od ucha k uchu', 'улы́бка до уше́й'), ('dať poza uši', 'дать в у́хо'), ('zapchať si uši', 'заткну́ть (себе́) у́ши'), ('jedným uchom tam, druhým von', 'в одно́ у́хо вошло́, в друго́е вы́шло, пропуска́ть ми́мо уше́й'), ('počúvať čo na pol ucha', 'вполу́ха слу́шать что'), ('neveriť vlastným ušiam', 'не ве́рить свои́м уша́м'), ('byť zamilovaný až po uši', 'влюби́ться по́ уши'), ('čapica s ušami', 'ша́пка с уша́ми, уша́нка'), ('ucho kabelky', 'ру́чка су́мки'), ('(pren.) oslie uši (v knihe)', 'заги́б страни́цы, за́гнутые углы́ страни́ц'), ('zamilovať sa po uši', 'влюби́ться по́ уши'), ('(anat.) stredné ucho', 'сре́днее у́хо'), ('šepkať čo do ucha komu', 'шепта́ть что на́ ухо кому'), ('hučanie v ušiach', 'гуде́ние в уша́х'), ('sčervenieť až po uši', 'покрасне́ть до уше́й'), ('strihať ušami', 'шевели́ть/прясть уша́ми'), ('šepkať do ucha', 'шепта́ть на́ ухо'), ('šuškať do ucha', 'шепта́ть на́ ухо'), ('s odretými ušami', 'с грехо́м попола́м'), ('Počul som to na vlastné uši.', 'Я э́то слы́шал со́бственными уша́ми.'), ('úsmev od ucha k uchu', 'рот до уше́й'), ('neveriť vlastným ušiam', 'не ве́рить со́бственным уша́м'), ('вну́треннее у́хо', 'vnútorné ucho'), ('повести́ уша́ми', 'strihnúť ušami'), ('слу́шать с пя́того на деся́тое', 'počúvať jedným uchom dnu, druhým von, počúvať každé piate slovo'), ('вну́треннее/сре́днее/нару́жное у́хо', 'vnútorné/stredné/vonkajšie ucho'), ('во все у́ши слу́шать', 'byť samé ucho , pozorne počúvať'), ('у́шки на маку́шке у кого', 'natŕča uši , zbystruje pozornosť'), ('(У меня́) гуди́т в у́шах.', 'Hučí mi v ušiach.'), ('шуми́т в у́шах', 'šumí v ušiach'), ('не ве́рить свои́м уша́м', 'neveriť vlastným ušiam'), ('втре́скаться по уши', 'buchnúť sa po uši'), ('по́ уши в долга́х', '(byť) po uši zadlžený'), ('По́сле дра́ки кулака́ми не ма́шут.', 'Neskoro zajaca chytať za chvost (keď si ho za uši nechytil).'), ('кра́ем у́ха слу́шать что', 'počúvať čo na pol ucha'), ('У стен есть у́ши.', 'Aj steny majú uši.')])

    actual = parse(source)
    assert actual is not None

    for (actual_translation, expected_translation) in zip(actual.translations, expected.translations):
        assert actual_translation == expected_translation
        
    for (actual_example, expected_example) in zip(actual.examples, expected.examples):
        assert actual_example == expected_example
