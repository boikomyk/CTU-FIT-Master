package controllers


import forms.NoteForm
import models.data.Note
import models.repositories.NotesRepository
import play.api.data.Form

import javax.inject._
import play.api.i18n.I18nSupport
import play.api.libs.json.Json
import play.api.mvc._
import services.ExporterService

import scala.collection.mutable.ListBuffer

/**
 * This controller creates an `Action` to handle HTTP requests to the
 * application's home page.
 */
@Singleton
class NotesController @Inject()(val controllerComponents: ControllerComponents, val notesRepository: NotesRepository, val exporter: ExporterService) extends BaseController with I18nSupport {

  /**
   * Create an Action to render an HTML page.
   *
   * The configuration in the `routes` file means that this method
   * will be called when the application receives a `GET` request with
   * a path of `/`.
   */

  /**
   * GET: Notes list
   */
  def notesList(): Action[AnyContent] = Action { implicit request: Request[AnyContent] =>
    Ok(views.html.notes_list(notesRepository.findAllNotes()))
  }

  /**
   * GET: Note detail
   *
   * @param id : Long
   */
  def noteDetail(id: Long): Action[AnyContent] = Action {
    implicit request => {
      val note: Option[Note] = notesRepository.findNoteById(id)
      if (note.isEmpty) {
        BadRequest("Note with such id does not exist, id: " + id)
      }

      // fill form with according values
      val form = NoteForm.form.fill(
        NoteForm(note.get.title, note.get.content, note.get.tags)
      );
      Ok(views.html.note_detail(note.get, form))
    }
  }

  /**
   * GET: Note edit
   *
   * @param id : Long
   */
  def noteEdit(id: Long): Action[AnyContent] = Action {
    implicit request => {
      val note: Option[Note] = notesRepository.findNoteById(id)
      if (note.isEmpty) {
        BadRequest("Note with such id does not exist, id: " + id)
      }

      // fill form with according values
      val form = NoteForm.form.fill(
        NoteForm(note.get.title, note.get.content, note.get.tags)
      );
      Ok(views.html.note_edit(note.get, form))
    }
  }

  /**
   * POST: Note edit, form processing
   *
   * @param id : Long
   */
  def noteEditPost(id: Long): Action[AnyContent] = Action {
    implicit request => {
      val note: Option[Note] = notesRepository.findNoteById(id)
      if (note.isEmpty) {
        BadRequest("Note with such id does not exist, id: " + id)
      }

      // form processing
      val bindForm: Form[NoteForm] = NoteForm.form.bindFromRequest()
      bindForm.fold(
        // form error handler
        (formWithErrors: Form[NoteForm]) => {
          BadRequest(views.html.note_edit(note.get, formWithErrors))
        },
        // update existed note
        (noteForm: NoteForm) => {
          notesRepository.updateNote(Note(Some(id), noteForm.title, noteForm.content, noteForm.tags.trim()))
          Redirect(routes.NotesController.noteDetail(id)).flashing(
            "success" -> ("[ID:" + id.toString + "] Note has been successfully updated")
          )
        }
      )
    }
  }

  /**
   * POST: Note delete
   *
   * @param id : Long
   * @return
   */
  def noteDelete(id: Long): Action[AnyContent] = Action {
    implicit request => {
      val note: Option[Note] = notesRepository.findNoteById(id)
      if (note.isEmpty) {
        BadRequest("Note with such id does not exist, id: " + id)
      }

      notesRepository.deleteNote(note.get)
      Redirect(routes.NotesController.notesList()).flashing(
        "success" -> ("[ID:" + id.toString + "] Note has been successfully removed")
      )
    }
  }

  /**
   * GET: Note new (new note creation)
   *
   * @return
   */
  def noteNew(): Action[AnyContent] = Action {
    implicit request => {
      Ok(views.html.note_new(NoteForm.form))
    }
  }

  /**
   * POST: Note new, form processing
   *
   * @return
   */
  def noteNewPost(): Action[AnyContent] = Action {
    implicit request => {
      // form processing
      val bindForm: Form[NoteForm] = NoteForm.form.bindFromRequest()
      bindForm.fold(
        // form error handler
        (formWithErrors: Form[NoteForm]) => {
          BadRequest(views.html.note_new(formWithErrors))
        },
        // create new db record
        (noteForm: NoteForm) => {
          notesRepository.saveNote(Note(
            title = noteForm.title,
            content = noteForm.content,
            tags = noteForm.tags.trim()
          ))
          Redirect(routes.NotesController.notesList()).flashing(
            "success" -> "Note has been successfully created"
          )
        }
      )
    }
  }

  /**
   * GET: Note export to CVS
   *
   * @return
   */
  def noteExportCSV(id: Long): Action[AnyContent] = Action {
    implicit request => {
      val note: Option[Note] = notesRepository.findNoteById(id)
      if (note.isEmpty) {
        BadRequest("Note with such id does not exist, id: " + id)
      }
      exporter.exportNoteToCSV(note.get, "note_" + note.get.id.get.toString)
    }
  }

  /**
   * GET: Notes batch export to CVS
   *
   * @return
   */
  def notesBatchExportCSV(): Action[AnyContent] = Action {
    implicit request => {
      val requestedIds = request.getQueryString("ids").get.split(',').map(_.trim.toLong)

      var requestedNotes = new ListBuffer[Note]()
      for(requestedId <- requestedIds) {
        val note: Option[Note] = notesRepository.findNoteById(requestedId)
        if (note.isEmpty) {
          BadRequest("Note with such id does not exist, id: " + requestedId.toString)
        }
        requestedNotes += note.get
      }
      exporter.exportNotesToCSV(requestedNotes.toList, "notes_batch_export")
    }
  }

  /**
   * POST: Upload note content from file
   * @return
   */
  def uploadNoteContent() = Action(parse.multipartFormData) { request =>
    request.body
      .file("file")
      .map { file =>
        val source = scala.io.Source.fromFile(file.ref.toFile.toString)
        val contentLines = try source.mkString finally source.close()

        Ok(Json.obj(
          "status" -> "OK",
          "content" -> contentLines,
        ))
      }
      .getOrElse {
        Ok(Json.obj(
          "status" -> "ERROR",
          "error" -> "Missing file",
        ))
      }
  }
}
