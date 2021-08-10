from flask import Blueprint, redirect, url_for, flash, request, render_template
from flask_login import login_required, current_user
from models.follow import Follow
from models.user import User

followers_blueprint = Blueprint("followers",
                                __name__,
                                template_folder="templates")


# follow user
@followers_blueprint.route("/create", methods=["POST"])
@login_required
def create():
    artist = User.get_or_none(User.id == request.form["artist"])
    follower = User.get_or_none(User.id == request.form["follower"])

    if artist and follower:
        # if artist account is public:
        if artist.public_profile:
            follow = Follow(artist=artist, follower=follower, approved=True)
            if follow.save():
                flash(f"You are now following {artist.username}.")
                return redirect(url_for("users.show",
                                        username=artist.username))
            else:
                flash(
                    f"Hmm, an error seems to have occurred. Please try again.")
                return redirect(url_for("users.show",
                                        username=artist.username))
        # if artist account is private:
        else:
            follow = Follow(artist=artist, follower=follower, approved=False)
            if follow.save():
                flash(
                    f"You have submitted a follow request to {artist.username}"
                )
                return redirect(url_for("users.show",
                                        username=artist.username))
            else:
                flash(
                    f"Hmm, an error seems to have occurred. Please try again.")
                return redirect(url_for("users.show",
                                        username=artist.username))


# unfollow user
@followers_blueprint.route("/remove", methods=["POST"])
@login_required
def destroy():
    artist = User.get_or_none(User.id == request.form["artist"])
    follower = User.get_or_none(User.id == request.form["follower"])
    follow_query = Follow.get_or_none(Follow.artist_id == artist.id
                                      and Follow.follower_id == follower.id)
    if follow_query.delete_instance():
        flash(f"You are no longer following {artist.username}")
        return redirect(url_for("users.show", username=artist.username))
    else:
        flash(f"Hmm, an error occurred. Please try again.")
        return redirect(url_for("users.show", username=artist.username))


# show follow requests
@followers_blueprint.route("/requests", methods=["GET"])
@login_required
def edit():
    user = User.get_or_none(User.username == current_user.username)
    followers = (User.select().join(
        Follow,
        on=Follow.follower_id == User.id).where((Follow.artist == user)
                                                & (Follow.approved == False)))
    return render_template("followers/edit.html",
                           user=user,
                           followers=followers)


# approve follow request
@followers_blueprint.route("/approve/<id>", methods=["POST"])
@login_required
def approve(id):
    follow_request = Follow.get_or_none(Follow.follower_id == id)
    follower = User.get_or_none(
        User.username == request.form["follower_username"])

    if follow_request:
        follow_request.approved = True
        if follow_request.save():
            flash(f"You have approved {follower.username}'s' follow request.")
            return redirect(url_for("followers.edit"))
        else:
            flash("Hmm, an error occurred. Please try again.")
            return redirect(url_for("followers.edit"))
    else:
        flash("Hmm, an error occured. Please try again.")
        return redirect(url_for("followers.edit"))


# delete follow request
@followers_blueprint.route("/delete/<id>", methods=["POST"])
@login_required
def delete(id):
    follow_request = Follow.get_or_none(Follow.follower_id == id)
    follower = User.get_or_none(
        User.username == request.form["follower_username"])

    if follow_request:
        if follow_request.delete_instance():
            flash(f"{follower.username}'s request has been denied.")
            return redirect(url_for("followers.edit"))
        else:
            flash("Hmm, an error occured. Please try again.")
            return redirect(url_for("followers.edit"))
    else:
        flash("Hmm, an error occured. Please try again.")
        return redirect(url_for("followers.edit"))