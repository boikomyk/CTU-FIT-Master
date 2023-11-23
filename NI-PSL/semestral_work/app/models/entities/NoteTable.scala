package models.entities

import models.data.Note
import org.joda.time.DateTime
import slick.jdbc.H2Profile.api._

import java.util.Date
//import slick.driver.H2Driver.api._

/**
 * Database for Note
 */


class NoteTable(tag: Tag) extends Table[Note](tag, "notes") {
  // mapper between the case class fields and the database columns
  override def * = (id.?, title, content, tags, createdWhen, updatedWhen) <> (Note.tupled, Note.unapply)
  // columns: id, name, content
  val id : Rep[Long] = column[Long]("id", O.AutoInc, O.PrimaryKey)
  val title: Rep[String] = column[String]("title")
  val content : Rep[String] = column[String]("content")
  val tags : Rep[String] = column[String]("tags")
  val createdWhen: Rep[java.time.LocalDateTime] = column[java.time.LocalDateTime]("created_when", O.SqlType("TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP"))
  val updatedWhen: Rep[java.time.LocalDateTime] = column[java.time.LocalDateTime]("updated_when", O.SqlType("TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
}
