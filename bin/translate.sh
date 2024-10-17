#!/usr/bin/env bash
TRANSLATIONS_DIR='app/translations'
CATALOGUE=$TRANSLATIONS_DIR/en/LC_MESSAGES/messages.pot
TARGET_LANGUAGE=cy
TARGET_MESSAGES=$TRANSLATIONS_DIR/$TARGET_LANGUAGE/LC_MESSAGES/messages.po
pybabel extract -F babel.cfg -k lazy_gettext -o $CATALOGUE . --no-location
if [ ! -f $TARGET_MESSAGES ]; then
    pybabel init -i $CATALOGUE -d $TRANSLATIONS_DIR -l $TARGET_LANGUAGE
fi
pybabel update -i $CATALOGUE -d $TRANSLATIONS_DIR -l $TARGET_LANGUAGE --no-fuzzy-matching --omit-header
pybabel compile -d $TRANSLATIONS_DIR -l $TARGET_LANGUAGE -f

printf "\n-----------------------IMPORTANT-----------------------\n"
echo "After updating $TARGET_MESSAGES. Run the following:"
echo "pybabel compile -d $TRANSLATIONS_DIR -l $TARGET_LANGUAGE -f"
printf "\n--------------------------------------------------------\n"