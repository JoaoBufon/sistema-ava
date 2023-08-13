from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.openapi.utils import get_openapi
from models import Curso, Aluno
from database import engine, Base, get_db
from repositories import CursoRepository, AlunoRepository
from schemas import CursoRequest, CursoResponse, AlunoRequest, AlunoResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/cursos", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
def create(request: CursoRequest, db: Session = Depends(get_db)):
    curso = CursoRepository.save(db, Curso(**request.dict()))
    return CursoResponse.from_orm(curso)

@app.post("/api/alunos", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED)
def create(request: AlunoRequest, db: Session = Depends(get_db)):
    aluno = AlunoRepository.save(db, Aluno(**request.dict()))
    return AlunoResponse.from_orm(aluno)

@app.get("/api/cursos", response_model=list[CursoResponse])
def find_all(db: Session = Depends(get_db)):
    cursos = CursoRepository.find_all(db)
    return [CursoResponse.from_orm(curso) for curso in cursos]

@app.get("/api/alunos", response_model=list[AlunoResponse])
def find_all(db: Session = Depends(get_db)):
    alunos = AlunoRepository.find_all(db)
    return [AlunoResponse.from_orm(aluno) for aluno in alunos]
    
@app.delete("/api/cursos/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curso(curso_id: int, db: Session = Depends(get_db)):
    if (CursoRepository.exists_by_id(db, curso_id)):
        CursoRepository.delete_by_id(db, curso_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado"
        )
    
@app.delete("/api/alunos/{aluno_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_aluno(aluno_id : int,db: Session = Depends(get_db)):
    if (AlunoRepository.exists_by_id(db, aluno_id)):
        if (CursoRepository.exists_by_id(db, AlunoRepository.find_by_id(db, aluno_id).id_curso)):
            if (not CursoRepository.find_by_id(db, AlunoRepository.find_by_id(db, aluno_id).id_curso).active):
                AlunoRepository.delete_by_id(db,aluno_id)
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            else:
                raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Aluno matriculado em curso ativo"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado"
        )
  
@app.get("/api/cursos/{curso_id}", response_model=CursoResponse)
def find_by_id(curso_id: int, db: Session = Depends(get_db)):
    if (CursoRepository.exists_by_id(db,curso_id)): 
        return CursoRepository.find_by_id(db,curso_id)
    else: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado"
        )
    
@app.get("/api/alunos/{aluno_id}", response_model=AlunoResponse)
def find_by_id(aluno_id : int,db: Session = Depends(get_db)):
    if (AlunoRepository.exists_by_id(db,aluno_id)): 
        return AlunoRepository.find_by_id(db,aluno_id)
    else: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado"
        )
    
@app.put("/api/cursos/{curso_id}", response_model=CursoResponse)
def editar_curso(curso_id: int, request: CursoRequest, db: Session = Depends(get_db)):
    if (CursoRepository.exists_by_id(db, curso_id)):
        return CursoRepository.save(db, Curso(id=curso_id, **request.dict()))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Curso não encontrado"
        )

@app.put("/api/alunos/{aluno_id}", response_model=AlunoResponse)
def editar_aluno(aluno_id: int, request: AlunoRequest, db: Session = Depends(get_db)):
    if (AlunoRepository.exists_by_id(db, aluno_id)):
        return AlunoRepository.save(db, Aluno(id=aluno_id, **request.dict()))
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado"
        )

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Ambiente Virtual de Aprendizagem",
        version="1.0.0",
        summary="Alunos EAD",
        description="Sistema de Ambiente Virtual de Aprendizagem para auxiliar alunos 100% EAD",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


