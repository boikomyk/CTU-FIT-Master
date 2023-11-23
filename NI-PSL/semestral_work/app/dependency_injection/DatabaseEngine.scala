package dependency_injection

import models.entities.NoteTable
import play.api.inject.ApplicationLifecycle
import slick.jdbc.H2Profile.api._
import slick.lifted.TableQuery

import javax.inject.{Inject, Singleton}
import scala.concurrent.Await
import scala.concurrent.duration.Duration


@Singleton
class DatabaseEngine @Inject()(lifecycle: ApplicationLifecycle) {
  val noteTable = TableQuery[NoteTable]
//  val dishes = TableQuery[Dishes]

  // create a connection to the database
  // var db can be used to execute queries on the database
  val db = Database.forConfig("h2mem")

  val setupFuture = db.run(
    noteTable.schema.createIfNotExists
  )
  Await.result(setupFuture, Duration.Inf)
}

