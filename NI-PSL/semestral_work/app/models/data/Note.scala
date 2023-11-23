package models.data

import java.time.LocalDateTime


/**
 * Note case class to model the data
 */
case class Note(id:Option[Long] = None, title:String, content:String, tags:String = "", created_when: java.time.LocalDateTime = LocalDateTime.now(), updated_when: java.time.LocalDateTime = LocalDateTime.now())

