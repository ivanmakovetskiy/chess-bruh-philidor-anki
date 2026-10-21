import os,json,io,hashlib,html,collections,concurrent.futures
import chess,chess.pgn,chess.svg,chess.engine,cairosvg,genanki
PROJECT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT=PROJECT+'/output';os.makedirs(ROOT+'/media',exist_ok=True)
G=json.load(open(PROJECT+'/data/account-games.json'))[50:]
def analyse(task):
 key,fen=task
 if not hasattr(analyse,'engine'):
  analyse.engine=chess.engine.SimpleEngine.popen_uci('/usr/games/stockfish');analyse.engine.configure({'Hash':32,'Threads':1})
  import multiprocessing.util
  multiprocessing.util.Finalize(analyse.engine,analyse.engine.quit,exitpriority=10)
 b=chess.Board(fen);info=analyse.engine.analyse(b,chess.engine.Limit(nodes=30000))
 pv=info['pv'];move=pv[0];san=b.san(move);piece=b.piece_at(move.from_square);parts=[]
 if b.is_check():parts.append('Responds to the check.')
 if b.is_castling(move):parts.append('Castles, bringing the rook into play and relocating the king.')
 elif b.is_capture(move):
  captured=b.piece_at(move.to_square);parts.append('Captures '+('a '+chess.piece_name(captured.piece_type) if captured else 'a pawn en passant')+'.')
 elif piece.piece_type==chess.PAWN:parts.append('Advances the '+chess.square_name(move.from_square)[0]+'-pawn to '+chess.square_name(move.to_square)+'.')
 else:parts.append('Repositions the '+chess.piece_name(piece.piece_type)+' from '+chess.square_name(move.from_square)+' to '+chess.square_name(move.to_square)+'.')
 bb=b.copy();bb.push(move)
 if bb.is_checkmate():parts.append('This is checkmate.')
 elif bb.is_check():parts.append('Gives check, forcing the opponent to address the king threat.')
 targets=[chess.square_name(s) for s in bb.attacks(move.to_square) if bb.piece_at(s) and bb.piece_at(s).color!=b.turn and bb.piece_at(s).piece_type!=chess.KING]
 if targets:parts.append('From '+chess.square_name(move.to_square)+', it attacks enemy material on '+', '.join(targets)+'. These attacks are not necessarily immediate wins.')
 score=info['score'].pov(b.turn)
 ev=('Mate in '+str(score.mate())+' ply-pairs (engine convention)' if score.is_mate() else f'{score.score()/100:+.2f} pawns')
 if score.is_mate():ev=('Forced mate in '+str(score.mate())+' moves' if score.mate()>0 else 'Facing forced mate in '+str(abs(score.mate()))+' moves')
 line=b.variation_san(pv[:8])
 path=ROOT+'/media/'+key+'.png'
 if not os.path.exists(path):
  svg=chess.svg.board(b,orientation=b.turn,size=360,coordinates=True,colors={'square light':'#f0d9b5','square dark':'#b58863'})
  cairosvg.svg2png(bytestring=svg.encode(),write_to=path)
 return key,{'move':san,'uci':move.uci(),'explanation':' '.join(parts),'evaluation':ev,'line':line,'depth':info.get('depth',0)}
positions={};rows=[];manifest=[]
with open(ROOT+'/philidor-games.pgn','w') as out:
 for i,g in enumerate(G,1):
  game=chess.pgn.read_game(io.StringIO(g['pgn']));assert not game.errors
  out.write(str(game)+'\n\n');b=game.board();ours=game.headers['White'].lower()=='redwinereduction';count=0
  player=g['white'] if ours else g['black'];rating=player['rating'];band=max(400,rating//100*100)
  for ply,m in enumerate(game.mainline_moves()):
   if b.turn==ours:
    fen=b.fen();key='ph_'+hashlib.sha256(fen.encode()).hexdigest()[:20];positions[key]=fen
    rows.append({'game':i,'ply':ply,'key':key,'fen':fen,'played':b.san(m),'played_uci':m.uci(),'color':'White' if ours else 'Black','move_number':b.fullmove_number,'opponent':game.headers['Black' if ours else 'White'],'url':g['url'],'rating':rating,'band':band});count+=1
   b.push(m)
  manifest.append({'game':i,'date':game.headers.get('Date'),'white':game.headers['White'],'black':game.headers['Black'],'rating':rating,'cards':count,'url':g['url']})
print('Games',len(G),'cards',len(rows),'unique positions',len(positions),flush=True)
cachefile=ROOT+'/analysis.json';results=json.load(open(cachefile)) if os.path.exists(cachefile) else {}
tasks=[p for p in positions.items() if p[0] not in results or not os.path.exists(ROOT+'/media/'+p[0]+'.png')]
with concurrent.futures.ProcessPoolExecutor(max_workers=6) as pool:
 for n,(k,v) in enumerate(pool.map(analyse,tasks,chunksize=10),1):
  results[k]=v
  if n%250==0:print('Analysed',n,'/',len(tasks),flush=True);json.dump(results,open(cachefile,'w'))
json.dump(results,open(cachefile,'w'))
model=genanki.Model(1945287101,'Philidor • Find the move',fields=[{'name':x} for x in ['ID','Board','Turn','Answer','Explanation','Line','EngineRecommendation','Evaluation','Source','FEN','Depth']],templates=[{'name':'Our turn','qfmt':'<div class="turn">{{Turn}} to move</div>{{Board}}<h3>What move was played here?</h3>','afmt':'{{FrontSide}}<hr id="answer"><div class="label">MOVE PLAYED</div><div class="answer">{{Answer}}</div><p class="small">The move played by redwinereduction — the answer to this card.</p><section class="engine"><h3>Stockfish supplement</h3><p><b>Engine recommendation:</b> {{EngineRecommendation}}</p><p>{{Explanation}}</p><p><b>Engine continuation:</b> {{Line}}</p><p><b>Engine evaluation (our perspective):</b> {{Evaluation}}</p><div class="small">The explanation and continuation above refer to the engine recommendation, not necessarily the move played. Stockfish 17 · 30,000 nodes · depth {{Depth}}. Other moves may also be good. These are generated board observations, not video commentary.</div></section><div class="small">{{Source}}<details><summary>FEN</summary>{{FEN}}</details></div>'}],css='.card{font-family:Arial,sans-serif;text-align:center;background:#f9f7f2;color:#252525;font-size:18px;padding:16px}.turn{font-weight:bold;margin-bottom:12px}img{width:360px;max-width:100%;height:auto}.answer{font-size:32px;font-weight:bold;color:#27694d}.small{font-size:13px;color:#777;line-height:1.5}p{line-height:1.5}a{color:#3676a0}')
decks={};e=html.escape
for r in rows:
 band=r['band'];deck=decks.setdefault(band,genanki.Deck(1945288000+band,f'Philidor Speedrun::Rating {band}–{band+99}'))
 v=results[r['key']];same=r['played_uci']==v['uci'];source=f'Game {r["game"]:} · vs {e(r["opponent"])} · move {r["move_number"]}<br><a href="{r["url"]}">Original game</a>'
 fields=[f'{r["game"]}-{r["ply"]}',f'<img src="{r["key"]}.png">',r['color'],e(r['played']),e(v['explanation']),e(v['line']),e(v['move']),e(v['evaluation']),source,e(r['fen']),str(v['depth'])]
 deck.add_note(genanki.Note(model=model,fields=fields,guid=genanki.guid_for('philidor',r['url'],r['ply']),tags=[f'game_{r["game"]:03}',r['color'].lower(),'engine_match' if same else 'engine_differs']))
pkg=genanki.Package(list(decks.values()));pkg.media_files=[ROOT+'/media/'+k+'.png' for k in positions];pkg.write_to_file(ROOT+'/Philidor-Speedrun.apkg')
json.dump(manifest,open(ROOT+'/manifest.json','w'),indent=2)
json.dump(rows,open(ROOT+'/positions.json','w'))
print('DONE',len(rows),'cards',len(positions),'boards',flush=True)
