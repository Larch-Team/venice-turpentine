from datetime import datetime
from close import Contradiction, Emptiness
from flask import Flask, render_template, request
from colors import COLORS, DEFAULT_COLOR
from engine import Session, contextdef_translate
from exceptions import EngineError, LrchLexerError
from flask_local.libs import JSONResponse, symbol_HTML, get_tree_clickable, get_tree_contra
from random import randint

app = Flask('flask_local', static_url_path='/static')
session = Session('main', 'config.json')

@app.route('/API/colors', methods=['GET'])
def colors():
    return COLORS | {'Czarny' : DEFAULT_COLOR}

@app.route('/', methods=['GET'])
def index():
    session.reset_proof()
    return render_template('index.html')


@app.route('/knowledge', methods=['GET'])
def knowledge():
    return render_template('knowledge-base.html', title="Baza wiedzy", text=session.acc('Assistant').get_articles()['Baza wiedzy'].text())


@app.route('/run', methods=['GET'])
def larch():
    return render_template('larch.html', hint_start="<div>"+"</div><div>".join(session.start_help())+"</div>")

# API


@app.route('/API/branchname', methods=['GET'])
def do_branch_name():
    return session.get_current_branch()


@app.route('/API/allbranch', methods=['GET'])
def do_all_branches():
    hjk = session.getbranches()
    return str(len(hjk))


@app.route('/API/jump', methods=['POST'])
def do_jump():
    where = request.json['branch']
    try:
        session.jump({'<': 'left', '>': 'right'}.get(where, where))
        return JSONResponse('success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/new_proof', methods=['POST'])
def do_new_proof():
    sentence = request.data.decode()
    if session.proof:
        session.reset_proof()
    try:
        text = session.new_proof(sentence)
    except (LrchLexerError, EngineError) as e:
        return JSONResponse(type_='error', content=str(e))
    else:
        if text:
            return JSONResponse(type_='error', content="\n".join(text))
        else:
            return JSONResponse('success')


@app.route('/API/use_rule', methods=['POST'])
def do_use_rule():
    rule = request.json['rule']
    context = request.json['context']

    # Check context
    context_info = session.context_info(rule)
    prepared = {}
    if context_info is None:
        return JSONResponse(type_='error', content="No such rule")
    for variable, official, _, type_ in context_info:
        if variable not in context:
            return JSONResponse(type_='error', content=f"{official} is not provided to the rule")

        vartype = contextdef_translate(type_)
        try:
            new = vartype(context[variable])
        except ValueError:
            return JSONResponse(type_='error', content=f"{official} is of a wrong type")

        prepared[variable] = new

    # Run use_rule
    try:
        text = session.use_rule(rule, prepared)
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))
    else:
        if text:
            return JSONResponse(type_='error', content="\n".join(text))
        else:
            return JSONResponse('success')


@app.route('/API/hint', methods=['GET'])
def do_hint() -> str:
    """Gives you a hint"""
    try:
        hints = session.hint()
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))
    if hints is not None:
        return JSONResponse(type_='success', content="".join(hints))
    else:
        return JSONResponse(type_='error', content="Podpowiedzi nie ma, trzymaj się tam")


@app.route('/API/randform', methods=['GET'])
def do_get_randform():
    try:
        return JSONResponse(type_='success', content=" ".join(session.gen_formula(randint(5, 10), randint(2, 5)).getLexems()))
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/worktree', methods=['GET'])
def do_get_worktree():
    if not session.proof:
        return "no proof"

    try:
        return get_tree_clickable(session.proof.nodes)
    except EngineError as e:
        return str(e)


@app.route('/API/contratree', methods=['GET'])
def do_get_contratree():
    if not session.proof:
        return "no proof"

    try:
        return get_tree_contra(session.proof.nodes)
    except EngineError as e:
        return f'<code>{e}</code>'


@app.route('/API/branch', methods=['GET'])
def do_get_branch():
    branch = request.args.get('branch', default=None, type=str)
    if not session.proof:
        return "no proof"

    try:
        session.jump(branch)
        return " ".join(
            f'<button class="branch-btn" id="btn{i}" onclick="forCheckBranch(\'{branch}\', {i});">{sen}</button>'
            for i, sen in enumerate(session.getbranch_strings()[0])
        )

    except EngineError as e:
        return f'<code>{e}</code>'


# @app.route('/API/preview', methods=['POST'])
# def do_preview():
#     rule = request.json['rule']
#     branch_name = request.json['branch']
#     context = request.json['context']
#     ret = session.proof.preview(branch_name, rule, context)
#     return get_preview(ret)


@app.route('/API/rules', methods=['GET'])
def do_get_rules():
    tokenID = request.args.get('tokenID', default=None, type=int)
    sentenceID = request.args.get('sentenceID', default=None, type=int)

    docs = session.getrules()
    if session.sockets['Formal'].plugin_name in ('analytic_freedom', 'analytic_signed') and session.proof is not None and sentenceID is not None and tokenID is not None:
        b, _ = session.proof.get_node().getbranch_sentences()
        br = b[sentenceID]
        try:
            token = br.getTypes()[tokenID]
        except IndexError:
            return ""
        docs = {i: j for i, j in docs.items() if i.endswith(token)}

    rules = session.getrulessymbol()
    return "".join(symbol_HTML(key, rules[key], tokenID, sentenceID, docs[key]) for key in docs)


@app.route('/API/undo', methods=['POST'])
def do_undo() -> str:
    """Undos last action"""
    try:
        rules = session.undo(1)
        return JSONResponse(type_='success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/no_contra', methods=['POST'])
def do_no_contra() -> str:
    branch_name = request.json['branch']
    try:
        _, closed = session.proof.nodes.getleaf(
            branch_name).getbranch_sentences()
        if closed:
            return JSONResponse(type_='error', content="Ta gałąź została już wcześniej zamknięta. Spróbuj inną.")
        session.proof.nodes.getleaf(branch_name).close(Emptiness)
        return JSONResponse(type_='success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/contra', methods=['POST'])
def do_contra() -> str:
    """Check contradiction"""
    try:
        branch_name = request.json['branch']
        sID1 = request.json['sentenceID1']
        sID2 = request.json['sentenceID2']
    except KeyError:
        return JSONResponse(type_='error', content="Musisz zaznaczyć formułę oraz jej negację, aby wykazać sprzeczność.")

    try:
        branch, closed = session.proof.nodes.getleaf(
            branch_name).getbranch_sentences()
        if closed:
            return JSONResponse(type_='error', content="Ta gałąź została już wcześniej zamknięta. Spróbuj inną.")
        elif session.sockets['Formal'].plugin_name == 'analytic_freedom':
            if (
                branch[sID1].getNonNegated() != branch[sID2].getNonNegated()
                or (
                    len(branch[sID1].reduceBrackets())
                    - len(branch[sID2].reduceBrackets())
                )
                % 2
                != 1
            ):
                return JSONResponse(type_='error', content="Podane formuły nie są ze sobą sprzeczne. Poszukaj innych, bądź uznaj gałąź za niesprzeczną.")
            session.proof.nodes.getleaf(branch_name).close(
                Contradiction(sentenceID1=sID1+1, sentenceID2=sID2+1))
            return JSONResponse(type_='success')
        elif session.sockets['Formal'].plugin_name == 'analytic_signed':
            if branch[sID1][1:] != branch[sID2][1:] or {
                branch[sID1].getTypes()[0],
                branch[sID2].getTypes()[0],
            } != {'signtrue', 'signfalse'}:
                return JSONResponse(type_='error', content="Podane formuły nie są ze sobą sprzeczne. Poszukaj innych, bądź uznaj gałąź za niesprzeczną.")
            session.proof.nodes.getleaf(branch_name).close(
                Contradiction(sentenceID1=sID1+1, sentenceID2=sID2+1))
            return JSONResponse(type_='success')
        else:
            session.proof.nodes.getleaf(branch_name).close(
                Contradiction(sentenceID1=sID1+1, sentenceID2=sID2+1))
            return JSONResponse(type_='success')
    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/save', methods=['GET'])
def do_save() -> str:
    name = request.args.get('name', default=str(
        datetime.now()).replace(':', '-'), type=int)
    return session.save_proof(name)


@app.route('/API/finish', methods=['POST'])
def do_finish() -> str:  # sourcery skip: merge-else-if-into-elif
    try:
        is_tautology = request.json['tautology']
        problems = [f"<p>{i}</p>" for i in session.check()]

        if problems:
            return JSONResponse(type_='error', content="\n".join(problems))

        test_proof = session.proof.copy()
        closed_branches = [i.branch for i in session.proof.nodes.getleaves(
        ) if i.closed and i.closed.success]

        # Check branch closure
        branches = []
        for i in test_proof.nodes.leaves:
            test_proof.closed = None
            test_proof.deal_closure(i.branch)
            if i.closed and i.closed.success and i.branch not in closed_branches:
                branches.append(
                    f'<p>Gałąź "{i.branch}" powinna zostać zamknięta.</p>')
        if branches:
            return JSONResponse(type_='error', content="\n".join(branches))

        # Check decision
        test_proof.solve()
        if is_tautology:
            if session.proof.nodes.is_successful():
                # Zaznaczono tautologię i poprawny dowód to wykazuje
                return JSONResponse(type_='success')
            elif test_proof.nodes.is_successful():
                # Zaznaczono tautologię, ale z dowodu to nie wynika, gdyż nie został dokończony
                return JSONResponse(type_='error', content='Ta formuła jest tautologią, choć może być tego nie widać z aktualnego dowodu. Spróbuj na przyszłość rozłożyć wszystkie formuły.')
            else:
                # Zaznaczono tautologię, gdy nie jest to tautologia i dowód to wykazuje
                return JSONResponse(type_='error', content='Ta formuła nie jest tautologią, a mimo to uznałeś ją za taką. Pamiętaj, że wszystkie gałęzie muszą być sprzeczne, aby dowieść formułę.')
        else:
            if session.proof.nodes.is_successful():
                # Zaznaczono nie-tautologię, gdy jest to tautologia i dowód to wykazuje
                return JSONResponse(type_='error', content='Ta formuła jest tautologią, a mimo to uznałeś ją za nietautologię. Pamiętaj, że wszystkie gałęzie muszą być sprzeczne, aby dowieść formułę.')
            elif test_proof.nodes.is_successful():
                # Zaznaczono nie-tautologię, ale formuła jest tautologią, ale dowód nie został dokończony
                return JSONResponse(type_='error', content='Ta formuła faktycznie nie jest tautologią, ale na przyszłość postaraj się wykazać to wyczerpując rozłożenia na wszystkich gałęziach.')
            else:
                # Zaznaczono nie-tautologię i poprawny dowód to wykazuje
                return JSONResponse(type_='success')

    except EngineError as e:
        return JSONResponse(type_='error', content=str(e))


@app.route('/API/print', methods=['GET'])
def do_print() -> str:
    old_plug = session.sockets['Output'].get_plugin_name()
    try:
        session.plug_switch('Output', request.args.get(
            'plugin', default='TeX_forest', type=str))
        t = "\n".join(session.gettree())
    finally:
        session.plug_switch('Output', old_plug)
    return t
