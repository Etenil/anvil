def brush(filename):
    exts = ((['as3'], 'as3'),
            (['sh', 'bash'], 'bash'),
            (['cf'], 'cf'),
            (['cpp', 'cc', 'c', 'h', 'hh', 'hpp', 's'], 'c'),
            (['cs'], 's-sharp'),
            (['css'], 'css'),
            (['pas'], 'pascal'),
            (['diff', 'patch'], 'diff'),
            (['erl'], 'erlang'),
            (['groovy', 'gvy', 'gy', 'gsh'], 'groovy'),
            (['java'], 'java'),
            (['jfx', 'javafx'], 'jfx'),
            (['js', 'jscript'], 'jscript'),
            (['pl'], 'pl'),
            (['php', 'php4', 'php5', 'inc', 'phtml'], 'php'),
            (['py'], 'python'),
            (['rb', 'rhtml', 'rjs'], 'ruby'),
            (['sca', 'scb', 'ssp'], 'scala'),
            (['sql'], 'sql'),
            (['vb', 'vbs', 'vbscript'], 'vb'),
            (['xml', 'html', 'xhtml', 'xslt', 'htm'], 'html'))
    default_ext = 'text'

    for e in exts:
        print e[0]
        for fileext in e[0]:
            print fileext
            if filename.endswith(fileext):
                print "filename ends with %s" % fileext
                return e[1]
    return default_ext
