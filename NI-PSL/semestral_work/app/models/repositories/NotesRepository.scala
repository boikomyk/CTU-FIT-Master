package models.repositories

import models.data.Note
import models.entities.NoteTable
import slick.lifted.TableQuery
import slick.jdbc.H2Profile.api._

import java.time.LocalDateTime

class NotesRepository extends AbstractRepository {
  var noteTable = TableQuery[NoteTable]

  def saveNote(note: Note): Unit = {
    save(noteTable += note)
  }

  def updateNote(note: Note): Unit = {
    save(
      noteTable.filter(_.id === note.id.get).
        map(o => (o.title, o.content, o.tags, o.updatedWhen)).
        update((note.title, note.content, note.tags, LocalDateTime.now()))
    )
  }

  def deleteNote(note: Note): Unit = {
    save(
      noteTable.filter(_.id === note.id.get).delete
    )
  }

  def findAllNotes(): Seq[Note] = {
    findAll(noteTable.result)
  }

  def findNoteById(id: Long): Option[Note] = {
    findById(noteTable.filter(_.id === id).result)
  }
}
