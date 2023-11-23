package forms

import play.api.data.Form
import play.api.data.Forms.{default, mapping, nonEmptyText, text}

// case class that will hold our form data
case class NoteForm(title: String, content: String, tags: String)

object NoteForm {
  val form: Form[NoteForm] = Form(
    // tell how to map between a form data and our new case class
    mapping(
      "title" -> nonEmptyText,
      "content" -> nonEmptyText,
      "tags" -> default(text, "")

    )(NoteForm.apply)(NoteForm.unapply)
  )
}
