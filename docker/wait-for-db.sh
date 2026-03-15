#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z $1 5432; do
  sleep 1
done

echo "PostgreSQL started"