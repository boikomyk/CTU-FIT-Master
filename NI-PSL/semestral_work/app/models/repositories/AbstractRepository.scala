package models.repositories


import slick.jdbc.H2Profile.api._
import slick.sql.{FixedSqlAction, FixedSqlStreamingAction}

import scala.concurrent.Await
import scala.concurrent.duration.Duration


class AbstractRepository {
  val dbPath = "h2mem"

  def save(action: FixedSqlAction[Int, NoStream, Effect.Write]): Int = {
    val db = Database.forConfig(dbPath)
    try {
      val future = {
        db.run(
          action
        )
      }
      Await.result(future, Duration.Inf)
    } finally db.close
  }

  def findAll[T](action: FixedSqlStreamingAction[Seq[T], T, Effect.Read]): Seq[T] = {
    val db = Database.forConfig(dbPath)
    try {
      val future = {
        db.run(
          action
        )
      }
      Await.result(future, Duration.Inf)
    } finally db.close
  }

  def findById[T](action: FixedSqlStreamingAction[Seq[T], T, Effect.Read]): Option[T] = {
    val db = Database.forConfig(dbPath)

    try {
      val future = {
        db.run(
          action
        )
      }
      val result: Seq[T] = Await.result(future, Duration.Inf)
      Option(result.last)
    } finally db.close
  }
}
